<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace2bconf.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace2bconf.sh

Purpose: this script inspects live tracefs/debugfs ftrace state and emits a bootconfig representation to stdout. It is the inverse companion to `bconf2ftrace.sh`, with explicit warnings for ftrace settings that cannot be faithfully recovered.

Important APIs/functions: `emit_kv()` prints bootconfig assignments. `global_options()` captures graph depth and warns about expanded graph filters. `kprobe_event_options()` and `synth_event_options()` export dynamic events. `per_event_options()`, `event_options()`, and `instance_options()` walk events and instances. Helper-variable tracking uses `defined_vars()`, `referred_vars()`, `DEFINED_VARS`, `UNRESOLVED_EVENTS`, and `retry_unresolved()` to delay histogram triggers that reference variables defined by other events.

Control flow: after option parsing and tracefs discovery, the script emits global kernel options, root `ftrace` instance options, and then each directory under `$TRACEFS/instances`. For each instance it emits non-default trace options, non-local trace clock, buffer size, snapshot allocation, CPU mask, tracing_on off state, current tracer, warnings for unsupported ftrace filters, and event configuration. Event traversal emits global/group enablement, per-event trigger actions, enable flags when not inherited, and filters. Unresolved histogram dependencies are retried up to three times.

State and persistence: it does not mutate tracefs; it reads live files and emits text. Its transient state is shell variables tracking histogram-defined and unresolved variables. The emitted bootconfig can later be persisted by redirecting stdout or applied with `bconf2ftrace.sh`.

Dependencies and integration points: it requires tracefs/debugfs, standard shell utilities, and ftrace file formats. The output schema is consumed by `bconf2ftrace.sh`. It intentionally cannot preserve wildcard expressions for graph/ftrace filters after the kernel expands them.

Risks: live ftrace state can change during traversal, so output is not atomic. `ls`-based traversal and unquoted paths assume conventional event and instance names. Trigger parsing treats non-comment trigger lines as opaque action strings but still has special histogram variable dependency logic based on regexes, which may miss complex trigger syntax. Return kprobes are skipped with a warning. Non-`kprobes` dynamic kprobe group names are normalized to `kprobes`, losing the original group. Unsupported wildcard filters produce warnings rather than output.

Test signals: round-trip tests should initialize ftrace, apply bootconfig, dump back to bootconfig, and compare normalized output for trace options, clocks, buffers, event enables, filters, dynamic kprobes, synthetic events, and hist triggers. Tests should also assert warnings for return probes, expanded filters, unsupported graph filters, and unresolved histogram variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace2bconf.sh -->
