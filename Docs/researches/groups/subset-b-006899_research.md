# subset-b-006899 research

Grouped source-tree-aligned research for rvgen LTL monitor generation, virtio userspace/vhost tests and stubs, WMI/workqueue/writeback tools, initramfs build tooling, and common KVM support files. Each section is delimited for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2ba.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2ba.py

## Purpose

Implements rvgen's LTL parser and on-the-fly Buchi automaton construction. It accepts `RULE = <LTL spec>` plus optional uppercase subexpression assignments, normalizes temporal formulas, expands graph nodes using the Gerth-Peled-Vardi-Wolper algorithm, and returns atoms plus graph nodes for code generation.

## Important APIs, Types, and Functions

Source size: 567 lines, 13509 bytes. Functions/classes: t_error, GraphNode, __init__, expand, __lt__, ASTNode, __init__, __hash__, __eq__, __iter__, negate, expand, __str__, normalize, BinaryOp, __init__, __hash__, __iter__, plus 82 more. Python imports: ply.lex, ply.yacc, .automata.

## Control Flow and Data Flow

PLY lex/yacc tokenizes lowercase temporal operators, uppercase atom names, booleans, parentheses, and assignments. `parse_ltl()` parses assignments, locates `RULE`, substitutes named subexpressions, and returns an AST. `create_graph()` normalizes every reachable AST node, collects atomic variables, expands the initial node set, fixes node ids, links incoming/outgoing edges, and labels non-temporal state predicates.

## State and Persistence Behavior

AST and graph ids are class counters, while each `GraphNode` carries `incoming`, `outgoing`, `new`, `old`, `next`, `labels`, and `init` fields. No persistent files are written; all state is in memory and is consumed by `ltl2k.py`.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The grammar has limited precedence because binary productions start with `opd`, so ambiguous formulas depend on explicit parentheses. Negation and normalization mutate AST nodes in place, which makes object identity important for contradiction checks. Unsupported lowercase atom names and parser errors surface as `AutomataError` paths.

## Test Signals

Parser tests should cover literals, variables, nested parentheses, every operator, assignment substitution, missing `RULE`, comments, illegal characters, contradictory labels, `next` propagation, and known LTL formulas with expected Buchi graph size/labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2ba.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2k.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2k.py

## Purpose

Turns an LTL specification into generated kernel monitor C for rvgen. It subclasses `generator.Monitor`, calls `ltl2ba.create_graph()`, abbreviates atom names, and fills the LTL monitor template with state enums, atom enums, start-state logic, transition logic, and instrumentation placeholders.

## Important APIs, Types, and Functions

Source size: 277 lines, 8226 bytes. Functions/classes: line_len, break_long_line, build_condition_string, abbreviate_atoms, shorten, find_share_length, ltl2k, __init__, _fill_states, _fill_atoms, _fill_atoms_to_string, _fill_atom_values, _fill_transitions, _fill_start, fill_tracepoint_handlers_skel, fill_tracepoint_attach_probe, fill_tracepoint_detach_helper, fill_atoms_init, plus 5 more. Python imports: pathlib, ., ., .automata.

## Control Flow and Data Flow

Construction validates `MonitorType == per_task`, reads the spec file, builds the Buchi automaton, derives atom abbreviations, and chooses a model name. `_fill_start()` emits initial state selection, `_fill_transitions()` emits switch-based next-state calculation, `_fill_atom_values()` recursively emits boolean helper expressions, and `fill_main_c()` injects atom initialization skeleton code into the template.

## State and Persistence Behavior

Generated state is textual C derived from `self.atoms`, `self.atoms_abbr`, `self.ba`, and `self.ltl`. Runtime monitor state lives in kernel `struct ltl_monitor`; this Python module itself only persists generated source output through the rvgen generator framework.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Column breaking is heuristic and can split only on spaces. Atom abbreviation can collide for similarly named atoms. The tracepoint attach/detach skeleton contains TODO placeholders and the detach helper names `handle_sample_event`, which must be reconciled with generated handlers.

## Test Signals

Use golden-file generation for representative formulas, compile generated headers with `RV_MAX_BA_STATES` and `RV_MAX_LTL_ATOM` limits, check line-length handling, and verify generated transition predicates against the Buchi graph.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2k.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/Kconfig -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/Kconfig

## Purpose

`Kconfig` is an rvgen Kconfig template for generated runtime-verification monitors. It defines template config symbols (RV_MON_%%MODEL_NAME_UP%%) that are replaced with the model name when a monitor is generated.

## Important APIs, Types, and Functions

Source size: 9 lines, 193 bytes. Kconfig symbols: RV_MON_%%MODEL_NAME_UP%%.

## Control Flow and Data Flow

There is no runtime flow. rvgen copies the template, substitutes placeholders such as `%%MODEL_NAME_UP%%`, and kbuild consumes the resulting config entry.

## State and Persistence Behavior

Only generated Kconfig metadata persists. The selected config controls whether generated monitor objects are built.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Placeholder mismatch can create invalid Kconfig symbols or monitors that cannot be selected. Dependency drift from runtime-verification core configs breaks generated builds.

## Test Signals

Generate a sample monitor, run Kconfig parsing, enable/disable the generated symbol, and build the generated module or built-in object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/Kconfig -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/Kconfig

## Purpose

`Kconfig` is an rvgen Kconfig template for generated runtime-verification monitors. It defines template config symbols (RV_MON_%%MODEL_NAME_UP%%) that are replaced with the model name when a monitor is generated.

## Important APIs, Types, and Functions

Source size: 5 lines, 103 bytes. Kconfig symbols: RV_MON_%%MODEL_NAME_UP%%.

## Control Flow and Data Flow

There is no runtime flow. rvgen copies the template, substitutes placeholders such as `%%MODEL_NAME_UP%%`, and kbuild consumes the resulting config entry.

## State and Persistence Behavior

Only generated Kconfig metadata persists. The selected config controls whether generated monitor objects are built.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Placeholder mismatch can create invalid Kconfig symbols or monitors that cannot be selected. Dependency drift from runtime-verification core configs breaks generated builds.

## Test Signals

Generate a sample monitor, run Kconfig parsing, enable/disable the generated symbol, and build the generated module or built-in object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/main.c -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/main.c

## Purpose

`main.c` is an rvgen C/header template used to instantiate generated runtime-verification monitor code. It contains substitution tokens and skeleton integration points rather than final model logic.

## Important APIs, Types, and Functions

Source size: 35 lines, 779 bytes. Includes: linux/kernel.h, linux/module.h, linux/init.h, linux/rv.h, %%MODEL_NAME%%.h. Macros/defines: MODULE_NAME.

## Control Flow and Data Flow

Generated code includes linux/kernel.h, linux/module.h, linux/init.h, linux/rv.h, %%MODEL_NAME%%.h. rvgen replaces tokens such as `%%MODEL_NAME%%`, tracepoint skeletons, monitor class names, parent monitor references, and descriptions before kbuild compiles the output.

## State and Persistence Behavior

Runtime state is owned by generated `struct rv_monitor` instances and the selected monitor class. The template itself persists only as source-generation input.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Unreplaced placeholders, stale tracepoint handler names, wrong parent references, or missing generated headers cause compile failures. Manual instrumentation sections must be completed by the monitor author.

## Test Signals

Generate dot2k/container/ltl2k sample monitors, inspect for unresolved `%%...%%` tokens, compile them, and enable/disable the resulting rv monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/main.h -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/main.h

## Purpose

`main.h` is an rvgen C/header template used to instantiate generated runtime-verification monitor code. It contains substitution tokens and skeleton integration points rather than final model logic.

## Important APIs, Types, and Functions

Source size: 3 lines, 84 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Generated code includes none. rvgen replaces tokens such as `%%MODEL_NAME%%`, tracepoint skeletons, monitor class names, parent monitor references, and descriptions before kbuild compiles the output.

## State and Persistence Behavior

Runtime state is owned by generated `struct rv_monitor` instances and the selected monitor class. The template itself persists only as source-generation input.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Unreplaced placeholders, stale tracepoint handler names, wrong parent references, or missing generated headers cause compile failures. Manual instrumentation sections must be completed by the monitor author.

## Test Signals

Generate dot2k/container/ltl2k sample monitors, inspect for unresolved `%%...%%` tokens, compile them, and enable/disable the resulting rv monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/container/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/main.c -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/main.c

## Purpose

`main.c` is an rvgen C/header template used to instantiate generated runtime-verification monitor code. It contains substitution tokens and skeleton integration points rather than final model logic.

## Important APIs, Types, and Functions

Source size: 83 lines, 1757 bytes. Includes: linux/ftrace.h, linux/tracepoint.h, linux/kernel.h, linux/module.h, linux/init.h, linux/rv.h, rv/instrumentation.h, rv_trace.h, %%MODEL_NAME%%.h, rv/%%MONITOR_CLASS%%_monitor.h. Macros/defines: MODULE_NAME, RV_MON_TYPE.

## Control Flow and Data Flow

Generated code includes linux/ftrace.h, linux/tracepoint.h, linux/kernel.h, linux/module.h, linux/init.h, linux/rv.h, rv/instrumentation.h, rv_trace.h, %%MODEL_NAME%%.h, rv/%%MONITOR_CLASS%%_monitor.h. rvgen replaces tokens such as `%%MODEL_NAME%%`, tracepoint skeletons, monitor class names, parent monitor references, and descriptions before kbuild compiles the output.

## State and Persistence Behavior

Runtime state is owned by generated `struct rv_monitor` instances and the selected monitor class. The template itself persists only as source-generation input.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Unreplaced placeholders, stale tracepoint handler names, wrong parent references, or missing generated headers cause compile failures. Manual instrumentation sections must be completed by the monitor author.

## Test Signals

Generate dot2k/container/ltl2k sample monitors, inspect for unresolved `%%...%%` tokens, compile them, and enable/disable the resulting rv monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/trace.h -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/trace.h

## Purpose

`trace.h` is an rvgen C/header template used to instantiate generated runtime-verification monitor code. It contains substitution tokens and skeleton integration points rather than final model logic.

## Important APIs, Types, and Functions

Source size: 13 lines, 359 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Generated code includes none. rvgen replaces tokens such as `%%MODEL_NAME%%`, tracepoint skeletons, monitor class names, parent monitor references, and descriptions before kbuild compiles the output.

## State and Persistence Behavior

Runtime state is owned by generated `struct rv_monitor` instances and the selected monitor class. The template itself persists only as source-generation input.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Unreplaced placeholders, stale tracepoint handler names, wrong parent references, or missing generated headers cause compile failures. Manual instrumentation sections must be completed by the monitor author.

## Test Signals

Generate dot2k/container/ltl2k sample monitors, inspect for unresolved `%%...%%` tokens, compile them, and enable/disable the resulting rv monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/trace_hybrid.h -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/trace_hybrid.h

## Purpose

`trace_hybrid.h` is an rvgen C/header template used to instantiate generated runtime-verification monitor code. It contains substitution tokens and skeleton integration points rather than final model logic.

## Important APIs, Types, and Functions

Source size: 16 lines, 465 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Generated code includes none. rvgen replaces tokens such as `%%MODEL_NAME%%`, tracepoint skeletons, monitor class names, parent monitor references, and descriptions before kbuild compiles the output.

## State and Persistence Behavior

Runtime state is owned by generated `struct rv_monitor` instances and the selected monitor class. The template itself persists only as source-generation input.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Unreplaced placeholders, stale tracepoint handler names, wrong parent references, or missing generated headers cause compile failures. Manual instrumentation sections must be completed by the monitor author.

## Test Signals

Generate dot2k/container/ltl2k sample monitors, inspect for unresolved `%%...%%` tokens, compile them, and enable/disable the resulting rv monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/dot2k/trace_hybrid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k/main.c -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k/main.c

## Purpose

`main.c` is an rvgen C/header template used to instantiate generated runtime-verification monitor code. It contains substitution tokens and skeleton integration points rather than final model logic.

## Important APIs, Types, and Functions

Source size: 102 lines, 2419 bytes. Functions/classes: ltl_atoms_fetch. Includes: linux/ftrace.h, linux/tracepoint.h, linux/kernel.h, linux/module.h, linux/init.h, linux/rv.h, rv/instrumentation.h, rv_trace.h, %%MODEL_NAME%%.h, rv/ltl_monitor.h. Macros/defines: MODULE_NAME.

## Control Flow and Data Flow

Generated code includes linux/ftrace.h, linux/tracepoint.h, linux/kernel.h, linux/module.h, linux/init.h, linux/rv.h, rv/instrumentation.h, rv_trace.h, %%MODEL_NAME%%.h, rv/ltl_monitor.h. rvgen replaces tokens such as `%%MODEL_NAME%%`, tracepoint skeletons, monitor class names, parent monitor references, and descriptions before kbuild compiles the output.

## State and Persistence Behavior

Runtime state is owned by generated `struct rv_monitor` instances and the selected monitor class. The template itself persists only as source-generation input.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Unreplaced placeholders, stale tracepoint handler names, wrong parent references, or missing generated headers cause compile failures. Manual instrumentation sections must be completed by the monitor author.

## Test Signals

Generate dot2k/container/ltl2k sample monitors, inspect for unresolved `%%...%%` tokens, compile them, and enable/disable the resulting rv monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k/trace.h -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k/trace.h

## Purpose

`trace.h` is an rvgen C/header template used to instantiate generated runtime-verification monitor code. It contains substitution tokens and skeleton integration points rather than final model logic.

## Important APIs, Types, and Functions

Source size: 14 lines, 480 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Generated code includes none. rvgen replaces tokens such as `%%MODEL_NAME%%`, tracepoint skeletons, monitor class names, parent monitor references, and descriptions before kbuild compiles the output.

## State and Persistence Behavior

Runtime state is owned by generated `struct rv_monitor` instances and the selected monitor class. The template itself persists only as source-generation input.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Unreplaced placeholders, stale tracepoint handler names, wrong parent references, or missing generated headers cause compile failures. Manual instrumentation sections must be completed by the monitor author.

## Test Signals

Generate dot2k/container/ltl2k sample monitors, inspect for unresolved `%%...%%` tokens, compile them, and enable/disable the resulting rv monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/templates/ltl2k/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/Makefile -->
# sources/distributed-fs/ceph-client/tools/virtio/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (CFLAGS +=, CFLAGS +=, LDFLAGS +=) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 58 lines, 2171 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/virtio/asm/barrier.h

## Purpose

`barrier.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (stdlib.h), macros (barrier, virt_mb, virt_rmb, virt_wmb, virt_store_mb, mb, dma_rmb, dma_wmb, dmb, virt_mb, virt_rmb, virt_wmb, plus 4 more), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 32 lines, 1128 bytes. Includes: stdlib.h. Macros/defines: barrier, virt_mb, virt_rmb, virt_wmb, virt_store_mb, mb, dma_rmb, dma_wmb, dmb, virt_mb, virt_rmb, virt_wmb, virt_store_mb, mb, dma_rmb, dma_wmb.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/asm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/crypto/hash.h -->
# sources/distributed-fs/ceph-client/tools/virtio/crypto/hash.h

## Purpose

`hash.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/crypto`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/crypto/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/generated/autoconf.h -->
# sources/distributed-fs/ceph-client/tools/virtio/generated/autoconf.h

## Purpose

`autoconf.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/generated`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/generated/autoconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/bug.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/bug.h

## Purpose

`bug.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (asm/bug.h), macros (_LINUX_BUG_H, BUG_ON, BUG), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 11 lines, 209 bytes. Includes: asm/bug.h. Macros/defines: _LINUX_BUG_H, BUG_ON, BUG.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/build_bug.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/build_bug.h

## Purpose

`build_bug.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (_LINUX_BUILD_BUG_H, BUILD_BUG_ON), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 7 lines, 151 bytes. Macros/defines: _LINUX_BUILD_BUG_H, BUILD_BUG_ON.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/build_bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/compiler.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/compiler.h

## Purpose

`compiler.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../../include/linux/compiler_types.h), macros (LINUX_COMPILER_H, __user, WRITE_ONCE, READ_ONCE, __aligned, data_race, __must_check), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 44 lines, 1511 bytes. Includes: ../../../include/linux/compiler_types.h. Macros/defines: LINUX_COMPILER_H, __user, WRITE_ONCE, READ_ONCE, __aligned, data_race, __must_check.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/cpumask.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/cpumask.h

## Purpose

`cpumask.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/kernel.h), macros (_LINUX_CPUMASK_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 11 lines, 192 bytes. Includes: linux/kernel.h. Macros/defines: _LINUX_CPUMASK_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/cpumask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/device.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/device.h

## Purpose

`device.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 10 lines, 111 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/dma-mapping.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/dma-mapping.h

## Purpose

`dma-mapping.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (_LINUX_DMA_MAPPING_H, dma_alloc_coherent, dma_free_coherent, dma_map_page, dma_map_page_attrs, dma_map_single, dma_map_single_attrs, dma_mapping_error, dma_unmap_single, dma_unmap_page, dma_unmap_page_attrs, sg_dma_address, plus 7 more), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 63 lines, 2157 bytes. Macros/defines: _LINUX_DMA_MAPPING_H, dma_alloc_coherent, dma_free_coherent, dma_map_page, dma_map_page_attrs, dma_map_single, dma_map_single_attrs, dma_mapping_error, dma_unmap_single, dma_unmap_page, dma_unmap_page_attrs, sg_dma_address, sg_dma_len, dma_need_sync, dma_unmap_single_attrs, dma_sync_single_range_for_cpu, dma_sync_single_range_for_device, dma_max_mapping_size, plus 1 more.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/dma-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/err.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/err.h

## Purpose

`err.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (ERR_H, MAX_ERRNO, IS_ERR_VALUE), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 27 lines, 564 bytes. Functions/classes: ERR_PTR, PTR_ERR, IS_ERR, IS_ERR_OR_NULL. Macros/defines: ERR_H, MAX_ERRNO, IS_ERR_VALUE.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/export.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/export.h

## Purpose

`export.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (EXPORT_SYMBOL_GPL, EXPORT_SYMBOL), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 3 lines, 105 bytes. Macros/defines: EXPORT_SYMBOL_GPL, EXPORT_SYMBOL.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/gfp.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/gfp.h

## Purpose

`gfp.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/topology.h), macros (__LINUX_GFP_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 7 lines, 120 bytes. Includes: linux/topology.h. Macros/defines: __LINUX_GFP_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/gfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/hrtimer.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/hrtimer.h

## Purpose

`hrtimer.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/hrtimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/irqreturn.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/irqreturn.h

## Purpose

`irqreturn.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../../include/linux/irqreturn.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 46 bytes. Includes: ../../../include/linux/irqreturn.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/irqreturn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/kernel.h

## Purpose

`kernel.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (stdbool.h, stdlib.h, stddef.h, stdio.h, string.h, assert.h, stdarg.h, linux/compiler.h, ../../../include/linux/container_of.h, linux/log2.h, linux/types.h, linux/overflow.h, plus 7 more), macros (KERNEL_H, CONFIG_SMP, PAGE_SIZE, PAGE_MASK, PAGE_ALIGN, READ, WRITE, virt_to_phys, phys_to_virt, page_to_phys, virt_to_page, offset_in_page, plus 13 more), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 160 lines, 3601 bytes. Functions/classes: kfree, free_pages_exact, __get_free_page, free_page, is_vmalloc_addr, synchronize_rcu. Includes: stdbool.h, stdlib.h, stddef.h, stdio.h, string.h, assert.h, stdarg.h, linux/compiler.h, ../../../include/linux/container_of.h, linux/log2.h, linux/types.h, linux/overflow.h, linux/limits.h, linux/list.h, linux/printk.h, linux/bug.h, errno.h, unistd.h, plus 1 more. Macros/defines: KERNEL_H, CONFIG_SMP, PAGE_SIZE, PAGE_MASK, PAGE_ALIGN, READ, WRITE, virt_to_phys, phys_to_virt, page_to_phys, virt_to_page, offset_in_page, __printf, ARRAY_SIZE, likely, unlikely, pr_err, pr_debug, plus 7 more.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kmemleak.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/kmemleak.h

## Purpose

`kmemleak.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 3 lines, 56 bytes. Functions/classes: kmemleak_ignore.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kmemleak.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kmsan.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/kmsan.h

## Purpose

`kmsan.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/gfp.h), macros (_LINUX_KMSAN_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 12 lines, 240 bytes. Functions/classes: kmsan_handle_dma. Includes: linux/gfp.h. Macros/defines: _LINUX_KMSAN_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/kmsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/mm_types.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/mm_types.h

## Purpose

`mm_types.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 3 lines, 43 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/mm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/module.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/module.h

## Purpose

`module.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/export.h), macros (MODULE_LICENSE, MODULE_AUTHOR, MODULE_DESCRIPTION), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 16 lines, 346 bytes. Includes: linux/export.h. Macros/defines: MODULE_LICENSE, MODULE_AUTHOR, MODULE_DESCRIPTION.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/printk.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/printk.h

## Purpose

`printk.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../../include/linux/kern_levels.h), macros (printk, vprintk), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 4 lines, 95 bytes. Includes: ../../../include/linux/kern_levels.h. Macros/defines: printk, vprintk.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/ratelimit.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/ratelimit.h

## Purpose

`ratelimit.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (DEFINE_RATELIMIT_STATE, __ratelimit), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 4 lines, 109 bytes. Macros/defines: DEFINE_RATELIMIT_STATE, __ratelimit.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/ratelimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/scatterlist.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/scatterlist.h

## Purpose

`scatterlist.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/kernel.h, linux/bug.h), macros (SCATTERLIST_H, sg_is_chain, sg_is_last, sg_chain_ptr, for_each_sg), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 173 lines, 4285 bytes. Functions/classes: sg_assign_page, sg_set_page, sg_chain, sg_mark_end, sg_unmark_end, sg_init_table, sg_phys, sg_set_buf, sg_init_one. Includes: linux/kernel.h, linux/bug.h. Macros/defines: SCATTERLIST_H, sg_is_chain, sg_is_last, sg_chain_ptr, for_each_sg.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/scatterlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/slab.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/slab.h

## Purpose

`slab.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (GFP_KERNEL, GFP_ATOMIC, __GFP_NOWARN, __GFP_ZERO), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 7 lines, 153 bytes. Macros/defines: GFP_KERNEL, GFP_ATOMIC, __GFP_NOWARN, __GFP_ZERO.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/slab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/spinlock.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/spinlock.h

## Purpose

`spinlock.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (pthread.h), macros (SPINLOCK_H_STUB), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 56 lines, 935 bytes. Functions/classes: spin_lock_init, spin_lock, spin_unlock, spin_lock_bh, spin_unlock_bh, spin_lock_irq, spin_unlock_irq, spin_lock_irqsave, spin_unlock_irqrestore. Includes: pthread.h. Macros/defines: SPINLOCK_H_STUB.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/thread_info.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/thread_info.h

## Purpose

`thread_info.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (check_copy_size), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 37 bytes. Macros/defines: check_copy_size.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/topology.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/topology.h

## Purpose

`topology.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/cpumask.h), macros (_LINUX_TOPOLOGY_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 7 lines, 151 bytes. Includes: linux/cpumask.h. Macros/defines: _LINUX_TOPOLOGY_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/uaccess.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/uaccess.h

## Purpose

`uaccess.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/compiler.h), macros (UACCESS_H, put_user, get_user), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 45 lines, 933 bytes. Functions/classes: volatile_memcpy, copy_from_user, copy_to_user. Includes: linux/compiler.h. Macros/defines: UACCESS_H, put_user, get_user.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/ucopysize.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/ucopysize.h

## Purpose

`ucopysize.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/bug.h), macros (__LINUX_UCOPYSIZE_H__), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 21 lines, 451 bytes. Functions/classes: check_object_size. Includes: linux/bug.h. Macros/defines: __LINUX_UCOPYSIZE_H__.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/ucopysize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/uio.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/uio.h

## Purpose

`uio.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/kernel.h, ../../../include/linux/uio.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 3 lines, 67 bytes. Includes: linux/kernel.h, ../../../include/linux/uio.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/uio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/virtio.h

## Purpose

`virtio.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../include/linux/virtio.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 40 bytes. Includes: ../../include/linux/virtio.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_byteorder.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_byteorder.h

## Purpose

`virtio_byteorder.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (asm/byteorder.h, ../../include/linux/byteorder/generic.h, ../../include/linux/virtio_byteorder.h), macros (_LINUX_VIRTIO_BYTEORDER_STUB_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 9 lines, 254 bytes. Includes: asm/byteorder.h, ../../include/linux/byteorder/generic.h, ../../include/linux/virtio_byteorder.h. Macros/defines: _LINUX_VIRTIO_BYTEORDER_STUB_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_config.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_config.h

## Purpose

`virtio_config.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../include/linux/virtio_config.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 47 bytes. Includes: ../../include/linux/virtio_config.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_ring.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_ring.h

## Purpose

`virtio_ring.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../../include/linux/virtio_ring.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 48 bytes. Includes: ../../../include/linux/virtio_ring.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/virtio_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/vringh.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/vringh.h

## Purpose

`vringh.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (limits.h, ../../../include/linux/vringh.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 2 lines, 63 bytes. Includes: limits.h, ../../../include/linux/vringh.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/vringh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/oot-stubs.h -->
# sources/distributed-fs/ceph-client/tools/virtio/oot-stubs.h

## Purpose

`oot-stubs.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/bug.h, linux/string.h, linux/virtio_features.h), macros (VIRTIO_FEATURES_BITS, VIRTIO_U64), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 10 lines, 223 bytes. Includes: linux/bug.h, linux/string.h, linux/virtio_features.h. Macros/defines: VIRTIO_FEATURES_BITS, VIRTIO_U64.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/oot-stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/Makefile -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (CFLAGS +=, CFLAGS +=, LDFLAGS +=) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 31 lines, 963 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.c

## Purpose

Provides the common two-thread benchmark harness for ring implementations in `tools/virtio/ringtest`. It parses options, creates eventfd-based kick/call channels, starts host and guest threads, and repeatedly drives the selected ring backend.

## Important APIs, Types, and Functions

Source size: 391 lines, 6532 bytes. Functions/classes: notify, wait_for_notify, kick, wait_for_kick, call, wait_for_call, set_affinity, poll_used, __attribute__, if, if, if, if, if, poll_avail, __attribute__, if, while, plus 4 more. Includes: getopt.h, pthread.h, assert.h, sched.h, main.h, sys/eventfd.h, stdlib.h, stdio.h, unistd.h, limits.h. Macros/defines: _GNU_SOURCE.

## Control Flow and Data Flow

The guest loop enqueues buffers until the run count or outstanding limit is reached, kicks in batches, drains completions, and either sleeps on call eventfd or polls. The host loop waits for available buffers, consumes them, optionally signals used buffers, and exits after the configured number of transfers.

## State and Persistence Behavior

Global knobs include `runcycles`, `max_outstanding`, `batch`, `param`, `do_sleep`, `do_relax`, `do_exit`, and `ring_size`. Ring-specific persistent state is owned by the linked backend implementation.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Assertions are used as error handling, invalid affinity or ring-size inputs abort, and sleep mode depends on backend notification functions being implemented. Benchmark results are sensitive to CPU affinity, cache sharing, eventfd overhead, and architecture-specific delay loops.

## Test Signals

Run each backend with polling and sleep modes, small/large rings, constrained outstanding counts, batching, host/guest affinity combinations, and architecture-specific relax/barrier paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.h -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.h

## Purpose

`main.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (assert.h, stdbool.h, x86intrin.h), macros (MAIN_H, VMEXIT_CYCLES, VMENTRY_CYCLES, VMEXIT_CYCLES, VMENTRY_CYCLES, VMEXIT_CYCLES, VMENTRY_CYCLES, barrier, cpu_relax, cpu_relax, cpu_relax, cpu_relax, plus 12 more), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 208 lines, 4797 bytes. Functions/classes: wait_cycles, wait_cycles, wait_cycles, vmexit, vmentry, busy_wait, __read_once_size, __write_once_size. Includes: assert.h, stdbool.h, x86intrin.h. Macros/defines: MAIN_H, VMEXIT_CYCLES, VMENTRY_CYCLES, VMEXIT_CYCLES, VMENTRY_CYCLES, VMEXIT_CYCLES, VMENTRY_CYCLES, barrier, cpu_relax, cpu_relax, cpu_relax, cpu_relax, smp_mb, smp_mb, smp_mb, smp_release, smp_acquire, smp_wmb, plus 6 more.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/noring.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/noring.c

## Purpose

`noring.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 72 lines, 971 bytes. Functions/classes: alloc_ring, used_empty, disable_call, enable_call, kick_available, disable_kick, enable_kick, avail_empty, use_buf, call_used. Includes: main.h, assert.h. Macros/defines: _GNU_SOURCE.

## Control Flow and Data Flow

Local functions/macros include alloc_ring, used_empty, disable_call, enable_call, kick_available, disable_kick, enable_kick, avail_empty, use_buf, call_used; includes are main.h, assert.h. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/noring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/ptr_ring.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/ptr_ring.c

## Purpose

`ptr_ring.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 209 lines, 3601 bytes. Functions/classes: kfree, spin_lock_init, spin_lock, spin_unlock, spin_lock_bh, spin_unlock_bh, spin_lock_irq, spin_unlock_irq, spin_lock_irqsave, spin_unlock_irqrestore, alloc_ring, add_inbuf, used_empty, disable_call, enable_call, kick_available, disable_kick, enable_kick, plus 3 more. Includes: main.h, stdlib.h, stdio.h, string.h, pthread.h, malloc.h, assert.h, errno.h, limits.h, ../../../include/linux/ptr_ring.h. Macros/defines: _GNU_SOURCE, SMP_CACHE_BYTES, cache_line_size, ____cacheline_aligned_in_smp, unlikely, likely, ALIGN, SIZE_MAX, KMALLOC_MAX_SIZE, __GFP_ZERO, kvmalloc_array, kvfree.

## Control Flow and Data Flow

Local functions/macros include kfree, spin_lock_init, spin_lock, spin_unlock, spin_lock_bh, spin_unlock_bh, spin_lock_irq, spin_unlock_irq, spin_lock_irqsave, spin_unlock_irqrestore, alloc_ring, add_inbuf, plus 9 more; includes are main.h, stdlib.h, stdio.h, string.h, pthread.h, malloc.h, assert.h, errno.h, limits.h, ../../../include/linux/ptr_ring.h. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/ptr_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/ring.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/ring.c

## Purpose

Implements a minimal descriptor ring benchmark backend with explicit ownership flags and event-index signaling. It is not the Linux virtio ring but a simplified cacheline-aware ring for comparing synchronization costs.

## Important APIs, Types, and Functions

Source size: 270 lines, 5946 bytes. Functions/classes: Copyright, alloc_ring, add_inbuf, used_empty, disable_call, kick_available, disable_kick, avail_empty, use_buf, call_used. Includes: main.h, stdlib.h, stdio.h, string.h. Macros/defines: _GNU_SOURCE, DESC_HW, HOST_GUEST_PADDING.

## Control Flow and Data Flow

Guest `add_inbuf()` fills descriptor address/length/data, publishes with release ordering by setting `DESC_HW`, and `get_buf()` reclaims descriptors once host clears the flag. Host `use_buf()` acquires the descriptor, decrements length to mark processing, releases the result, clears `DESC_HW`, and advances `used_idx`. Event helpers compare requested event indices with `need_event()`.

## State and Persistence Behavior

Shared state is split into padded `guest`, `host`, descriptor `ring`, `event`, and side `data` arrays to reduce false sharing. Indices wrap by `ring_size - 1`, requiring a power-of-two ring size.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Correctness depends on the paired barriers documented in comments. A non-power-of-two ring corrupts indexing. Notification suppression can create lost wakeups if event indices or memory ordering regress.

## Test Signals

Stress with sleep and polling, small rings, high batch sizes, weak-memory architectures, forced wraparound, and instrumentation that checks descriptor ownership transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/run-on-all.sh -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/run-on-all.sh

## Purpose

`run-on-all.sh` is a POSIX shell helper for the surrounding build/test flow.

## Important APIs, Types, and Functions

Source size: 26 lines, 670 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

It reads command-line arguments or system topology, constructs derived command lines, and invokes lower-level tools in a deterministic sequence.

## State and Persistence Behavior

State is shell variables and temporary files created during execution; persistent outputs are produced by invoked tools.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Shell word splitting and external command availability are the main risks. Paths with whitespace and architecture/topology assumptions need care.

## Test Signals

Run with representative arguments, missing inputs, unusual CPU topology or file names, and verify cleanup of temporary files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/run-on-all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_0_9.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_0_9.c

## Purpose

Implements a benchmark backend modeled on virtio 0.9 split rings, with optional `RING_POLL` and `INORDER` compile-time variants.

## Important APIs, Types, and Functions

Source size: 333 lines, 7155 bytes. Functions/classes: alloc_ring, add_inbuf, used_empty, disable_call, kick_available, disable_kick, avail_empty, use_buf, call_used. Includes: main.h, stdlib.h, stdio.h, assert.h, string.h, linux/virtio_ring.h. Macros/defines: _GNU_SOURCE, HOST_GUEST_PADDING.

## Control Flow and Data Flow

Guest allocates descriptors, writes avail entries or in-order state, publishes `avail->idx`, and later consumes used entries. Host reads available heads, translates descriptors, writes used entries or in-order lengths, publishes `used->idx`, and uses `vring_need_event()` for kicks/calls.

## State and Persistence Behavior

State spans `struct vring ring`, guest free-list/indices, host used indices, and side data tokens. `virtio_ring_poll.c` and `virtio_ring_inorder.c` include this file with feature defines to build alternate code paths.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The three variants share source and are mutually exclusive in assumptions. Barrier A/B/C/D pairs must match virtio split-ring visibility requirements. Ring polling encodes high bits in ids and can break if index masking changes.

## Test Signals

Build all variants, run wraparound and sleep-mode tests, compare notification counts, and test with and without outstanding limits on x86 and weaker memory-order architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_0_9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_inorder.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_inorder.c

## Purpose

`virtio_ring_inorder.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 2 lines, 47 bytes. Includes: virtio_ring_0_9.c. Macros/defines: INORDER.

## Control Flow and Data Flow

Local functions/macros include none; includes are virtio_ring_0_9.c. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_inorder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_poll.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_poll.c

## Purpose

`virtio_ring_poll.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 2 lines, 49 bytes. Includes: virtio_ring_0_9.c. Macros/defines: RING_POLL.

## Control Flow and Data Flow

Local functions/macros include none; includes are virtio_ring_0_9.c. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/uio.h -->
# sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/uio.h

## Purpose

`uio.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (sys/uio.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 21 bytes. Includes: sys/uio.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/uapi/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/uio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_config.h -->
# sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_config.h

## Purpose

`virtio_config.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../../../include/uapi/linux/virtio_config.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 58 bytes. Includes: ../../../../include/uapi/linux/virtio_config.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/uapi/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_ring.h -->
# sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_ring.h

## Purpose

`virtio_ring.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../../../include/uapi/linux/virtio_ring.h), macros (VIRTIO_RING_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 5 lines, 166 bytes. Includes: ../../../../include/uapi/linux/virtio_ring.h. Macros/defines: VIRTIO_RING_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/uapi/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_types.h -->
# sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_types.h

## Purpose

`virtio_types.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (../../include/uapi/linux/virtio_types.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 1 lines, 51 bytes. Includes: ../../include/uapi/linux/virtio_types.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/uapi/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/uapi/linux/virtio_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_net_test.c -->
# sources/distributed-fs/ceph-client/tools/virtio/vhost_net_test.c

## Purpose

Exercises `/dev/vhost-net` using a TAP device and raw packet socket. It verifies TX and RX packet movement through vhost-net with selectable virtio features and interrupt behavior.

## Important APIs, Types, and Functions

Source size: 532 lines, 11699 bytes. Functions/classes: tun_alloc, vdev_create_socket, vdev_send_packet, vq_notify, vhost_vq_setup, vq_reset, vq_info_add, vdev_info_init, wait_for_interrupt, verify_res_buf, run_tx_test, while, if, while, if, run_rx_test, while, if, plus 5 more. Includes: getopt.h, limits.h, string.h, poll.h, sys/eventfd.h, stdlib.h, assert.h, unistd.h, sys/ioctl.h, sys/stat.h, sys/types.h, fcntl.h, stdbool.h, linux/vhost.h, linux/if.h, linux/if_tun.h, linux/in.h, linux/if_packet.h, plus 2 more. Macros/defines: _GNU_SOURCE, HDR_LEN, TEST_BUF_LEN, TEST_PTYPE, DESC_NUM.

## Control Flow and Data Flow

The program creates a TAP with vnet headers, opens an AF_PACKET socket, prepares a loopback Ethernet payload, opens `/dev/vhost-net`, installs the memory table and feature bits, attaches queue backends, then runs TX by adding outbufs and RX by adding inbufs plus sending packets into the TAP.

## State and Persistence Behavior

`struct vdev_info` stores the virtio device, two queues, TAP/socket metadata, MAC address, test/result buffers, and vhost memory. Each `vq_info` tracks started/completed counts and eventfds.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Requires privileges, `/dev/net/tun`, `/dev/vhost-net`, and a usable networking namespace. Hardcoded packet type and one-buffer-at-a-time loops make it a correctness smoke test more than a full throughput tool.

## Test Signals

Run with event index, indirect, virtio-1 toggles, delayed interrupts, and varied buffer counts; verify payload bytes and lengths for both TX and RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_net_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_test/Makefile -->
# sources/distributed-fs/ceph-client/tools/virtio/vhost_test/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (obj-m +=) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 3 lines, 94 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/vhost_test`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_test/vhost_test.c -->
# sources/distributed-fs/ceph-client/tools/virtio/vhost_test/vhost_test.c

## Purpose

`vhost_test.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 1 lines, 18 bytes. Includes: test.c.

## Control Flow and Data Flow

Local functions/macros include none; includes are test.c. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/vhost_test`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_test/vhost_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/Makefile -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (CFLAGS =) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 14 lines, 246 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/virtio-trace`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent-ctl.c -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent-ctl.c

## Purpose

`trace-agent-ctl.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 135 lines, 2672 bytes. Functions/classes: signal_handler, rw_ctl_init, wait_order, while, if, if, while, if, if. Includes: fcntl.h, poll.h, signal.h, stdio.h, stdlib.h, unistd.h, trace-agent.h. Macros/defines: _GNU_SOURCE, HOST_MSG_SIZE, EVENT_WAIT_MSEC.

## Control Flow and Data Flow

Local functions/macros include signal_handler, rw_ctl_init, wait_order, while, if, if, while, if, if; includes are fcntl.h, poll.h, signal.h, stdio.h, stdlib.h, unistd.h, trace-agent.h. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/virtio-trace`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent-ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent-rw.c -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent-rw.c

## Purpose

`trace-agent-rw.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 190 lines, 4398 bytes. Functions/classes: Copyright, if, if, bind_cpu, while, if, if, rw_thread_run. Includes: fcntl.h, stdio.h, stdlib.h, unistd.h, sys/syscall.h, trace-agent.h. Macros/defines: _GNU_SOURCE, READ_WAIT_USEC.

## Control Flow and Data Flow

Local functions/macros include Copyright, if, if, bind_cpu, while, if, if, rw_thread_run; includes are fcntl.h, stdio.h, stdlib.h, unistd.h, sys/syscall.h, trace-agent.h. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/virtio-trace`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent-rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.c -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.c

## Purpose

`trace-agent.c` is part of the virtio userspace test/build support tree. It either implements a test binary or supplies local kernel-API stubs so in-kernel virtio/vhost code can be compiled and exercised from userspace.

## Important APIs, Types, and Functions

Source size: 272 lines, 5417 bytes. Functions/classes: get_total_cpus, if, parse_size, if, usage, if, if, while, agent_main_loop, if, agent_info_free, main. Includes: limits.h, stdio.h, stdlib.h, unistd.h, trace-agent.h. Macros/defines: _GNU_SOURCE, PAGE_SIZE, PIPE_DEF_BUFS, PIPE_MIN_SIZE, PIPE_MAX_SIZE, TRACEFS, DEBUGFS, READ_PATH_FMT, WRITE_PATH_FMT, CTL_PATH.

## Control Flow and Data Flow

Local functions/macros include get_total_cpus, if, parse_size, if, usage, if, if, while, agent_main_loop, if, agent_info_free, main; includes are limits.h, stdio.h, stdlib.h, unistd.h, trace-agent.h. Runtime C files generally set up rings, eventfds, vhost ioctls, or trace streams and then loop until configured transfers complete.

## State and Persistence Behavior

State lives in test-owned structures, userspace allocated vrings, eventfds, pthread locks, or fake kernel globals. No repository state is modified by normal test execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/virtio-trace`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test environment must match kernel headers and devices. Stubbed kernel APIs intentionally approximate behavior and can mask kernel-only lifetime or DMA issues.

## Test Signals

Compile the full `tools/virtio` target set, run ring/virtqueue/vhost tests with feature toggles, and check warning-free builds under the intended host compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.h -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.h

## Purpose

`trace-agent.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (pthread.h, stdbool.h), macros (__TRACE_AGENT_H__, MAX_CPUS, PIPE_INIT, pr_err, pr_info, pr_debug, pr_debug), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 76 lines, 2139 bytes. Includes: pthread.h, stdbool.h. Macros/defines: __TRACE_AGENT_H__, MAX_CPUS, PIPE_INIT, pr_err, pr_info, pr_debug, pr_debug.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/virtio-trace`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio-trace/trace-agent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio_test.c -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio_test.c

## Purpose

Userspace regression/performance test for kernel virtqueue code against `/dev/vhost-test`. It creates a synthetic virtio device, maps one vhost memory region, configures a vring, and sends many buffers through the vhost test backend.

## Important APIs, Types, and Functions

Source size: 403 lines, 9088 bytes. Functions/classes: vq_notify, vq_callback, vq_reset, vq_info_add, vdev_info_init, wait_for_interrupt, if, run_test, while, if, if, if, while, if, if, help, main, switch, plus 2 more. Includes: getopt.h, limits.h, string.h, poll.h, sys/eventfd.h, stdlib.h, assert.h, unistd.h, sys/ioctl.h, sys/stat.h, sys/types.h, fcntl.h, stdbool.h, linux/virtio_types.h, linux/vhost.h, linux/virtio.h, linux/virtio_ring.h, ../../drivers/vhost/test.h. Macros/defines: _GNU_SOURCE, RANDOM_BATCH.

## Control Flow and Data Flow

`vdev_info_init()` opens the control fd and installs memory. `vq_info_add()` allocates vring memory, creates a `virtqueue`, and programs vhost vring ioctls. `run_test()` disables callbacks, batches outbuf submissions, kicks the backend, drains completions, optionally resets backend/ring state, and waits using normal or delayed interrupts.

## State and Persistence Behavior

State is held in `struct vdev_info`, `struct vq_info`, eventfds, one guest memory buffer, vhost memory table, and feature bits for indirect descriptors, event index, and virtio 1.0.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test assumes `/dev/vhost-test` and matching kernel headers. Reset paths manipulate backend and vring base while transfers are active. All failures are assertion-based, so it is best as a developer smoke/regression test.

## Test Signals

Run with `--no-indirect`, `--no-event-idx`, `--no-virtio-1`, delayed interrupts, random batch sizes, and reset intervals; verify no lost completions or vhost ioctl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vringh_test.c -->
# sources/distributed-fs/ceph-client/tools/virtio/vringh_test.c

## Purpose

Comprehensive userspace test for host-side `vringh` helpers, including direct descriptors, indirect descriptors, split user address mappings, iov expansion, multi-completion, event index, and a parallel host/guest stress mode.

## Important APIs, Types, and Functions

Source size: 758 lines, 20556 bytes. Functions/classes: never_notify_host, never_callback_guest, getrange_iov, getrange_slow, parallel_notify_host, no_notify_host, find_cpus, if, vringh_get_head, parallel_test, if, while, if, if, if, if, if, if, plus 8 more. Includes: sched.h, err.h, linux/kernel.h, linux/err.h, linux/virtio.h, linux/vringh.h, linux/virtio_ring.h, linux/virtio_config.h, linux/uaccess.h, sys/types.h, sys/stat.h, sys/mman.h, sys/wait.h, fcntl.h. Macros/defines: _GNU_SOURCE, USER_MEM, RINGSIZE, ALIGN, NUM_XFERS.

## Control Flow and Data Flow

The non-parallel path creates a guest virtqueue and host `vringh` view over user memory, then tests descriptor fetch, pull/push, completion, large scatterlists, many completions, and unusual indirect descriptor layouts. `parallel_test()` mmaps the same file at different host/guest addresses, forks host and guest, exchanges notifications through pipes, and optionally uses a fast opencoded get-head path.

## State and Persistence Behavior

Global user address bounds and offset simulate translated user memory. Parallel state uses shared mmap rings/data, pipes, CPU affinity, `guest_virtio_device`, and notification counters.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test is intentionally aggressive: it forces allocations through fake kmalloc pointers, depends on `/tmp/vringh_test-file`, assumes enough descriptors, and uses many assertions. Mapping math and slow one-byte ranges are the key correctness stressors.

## Test Signals

Run base mode with `--indirect`, `--eventidx`, `--virtio-1`, `--slow-range`; run `--parallel` with and without `--fast-vringh`; check no descriptor leaks, bad lengths, or notification hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vringh_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/xen/xen.h -->
# sources/distributed-fs/ceph-client/tools/virtio/xen/xen.h

## Purpose

`xen.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (XEN_XEN_STUB_H, xen_domain), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 6 lines, 78 bytes. Macros/defines: XEN_XEN_STUB_H, xen_domain.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/xen`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/xen/xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/wmi/Makefile -->
# sources/distributed-fs/ceph-client/tools/wmi/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (CFLAGS +=, TARGET =) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 18 lines, 379 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/wmi`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/wmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/wmi/dell-smbios-example.c -->
# sources/distributed-fs/ceph-client/tools/wmi/dell-smbios-example.c

## Purpose

`dell-smbios-example.c` is source-tree support code in this subset. It contains 207 lines and contributes to the surrounding Linux/Ceph-client tooling or virtualization build.

## Important APIs, Types, and Functions

Source size: 207 lines, 4863 bytes. Functions/classes: show_buffer, run_wmi_smbios_cmd, find_token, token_is_active, query_token, activate_token, query_buffer_size, main, if. Includes: errno.h, fcntl.h, stdio.h, stdlib.h, sys/ioctl.h, unistd.h, linux/wmi.h. Macros/defines: __packed.

## Control Flow and Data Flow

Important local symbols include show_buffer, run_wmi_smbios_cmd, find_token, token_is_active, query_token, activate_token, query_buffer_size, main, if; includes are errno.h, fcntl.h, stdio.h, stdlib.h, sys/ioctl.h, unistd.h, linux/wmi.h. Control flow follows the surrounding tool's build or runtime entry points.

## State and Persistence Behavior

State is local to the surrounding tool or kernel subsystem and is not persisted by this file unless generated build outputs are produced.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/wmi`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Risks are mainly integration drift with adjacent headers, build flags, generated files, or kernel ABI expectations.

## Test Signals

Build the owning target and run subsystem smoke tests that exercise this file's exported symbols or generated artifact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/wmi/dell-smbios-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_dump.py -->
# sources/distributed-fs/ceph-client/tools/workqueue/wq_dump.py

## Purpose

`wq_dump.py` is a Python/drgn utility script for inspecting live kernel state. It imports/defines err, cpumask_str, wq_type_str, print_pod_type and reads kernel symbols through drgn to print operational diagnostics.

## Important APIs, Types, and Functions

Source size: 249 lines, 8554 bytes. Functions/classes: err, cpumask_str, wq_type_str, print_pod_type. Python imports: sys, drgn, drgn.helpers.linux.list, drgn.helpers.linux.percpu, drgn.helpers.linux.cpumask, drgn.helpers.linux.nodemask, drgn.helpers.linux.idr, argparse.

## Control Flow and Data Flow

Argument parsing builds filters and output mode, kernel objects are read from `prog`, helper functions format masks or stats, and the script either prints once or loops at the requested interval until interrupted.

## State and Persistence Behavior

The script stores only transient sampled values. Persistent state remains in the inspected kernel: workqueues, worker pools, backing-device writeback structures, or generated monitor inputs.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/workqueue`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

It depends on exact kernel symbol and struct names, BTF/debug info, and drgn helpers. Field layout changes or disabled configs can raise exceptions. JSON mode prints Python dict syntax in some scripts rather than strict serialized JSON.

## Test Signals

Run against a matching live kernel and vmcore, with and without filters, interval zero and repeated mode, and configs that disable optional NUMA/cgroup/writeback features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_dump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_monitor.py -->
# sources/distributed-fs/ceph-client/tools/workqueue/wq_monitor.py

## Purpose

`wq_monitor.py` is a Python/drgn utility script for inspecting live kernel state. It imports/defines WqStats, __init__, dict, table_header_str, table_row_str, sigint_handler, main and reads kernel symbols through drgn to print operational diagnostics.

## Important APIs, Types, and Functions

Source size: 168 lines, 6358 bytes. Functions/classes: WqStats, __init__, dict, table_header_str, table_row_str, sigint_handler, main. Python imports: signal, re, time, json, drgn, drgn.helpers.linux.list, argparse.

## Control Flow and Data Flow

Argument parsing builds filters and output mode, kernel objects are read from `prog`, helper functions format masks or stats, and the script either prints once or loops at the requested interval until interrupted.

## State and Persistence Behavior

The script stores only transient sampled values. Persistent state remains in the inspected kernel: workqueues, worker pools, backing-device writeback structures, or generated monitor inputs.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/workqueue`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

It depends on exact kernel symbol and struct names, BTF/debug info, and drgn helpers. Field layout changes or disabled configs can raise exceptions. JSON mode prints Python dict syntax in some scripts rather than strict serialized JSON.

## Test Signals

Run against a matching live kernel and vmcore, with and without filters, interval zero and repeated mode, and configs that disable optional NUMA/cgroup/writeback features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/workqueue/wq_monitor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/writeback/wb_monitor.py -->
# sources/distributed-fs/ceph-client/tools/writeback/wb_monitor.py

## Purpose

`wb_monitor.py` is a Python/drgn utility script for inspecting live kernel state. It imports/defines K, Stats, dict, table_header_str, table_row_str, show_header, show_stats, WbStats, __init__, BdiStats, __init__, collectStats, plus 2 more and reads kernel symbols through drgn to print operational diagnostics.

## Important APIs, Types, and Functions

Source size: 172 lines, 5413 bytes. Functions/classes: K, Stats, dict, table_header_str, table_row_str, show_header, show_stats, WbStats, __init__, BdiStats, __init__, collectStats, sigint_handler, main. Python imports: signal, re, time, json, drgn, drgn.helpers.linux.list, argparse.

## Control Flow and Data Flow

Argument parsing builds filters and output mode, kernel objects are read from `prog`, helper functions format masks or stats, and the script either prints once or loops at the requested interval until interrupted.

## State and Persistence Behavior

The script stores only transient sampled values. Persistent state remains in the inspected kernel: workqueues, worker pools, backing-device writeback structures, or generated monitor inputs.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/writeback`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

It depends on exact kernel symbol and struct names, BTF/debug info, and drgn helpers. Field layout changes or disabled configs can raise exceptions. JSON mode prints Python dict syntax in some scripts rather than strict serialized JSON.

## Test Signals

Run against a matching live kernel and vmcore, with and without filters, interval zero and repeated mode, and configs that disable optional NUMA/cgroup/writeback features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/writeback/wb_monitor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/Kconfig -->
# sources/distributed-fs/ceph-client/usr/Kconfig

## Purpose

`Kconfig` is source-tree support code in this subset. It contains 229 lines and contributes to the surrounding Linux/Ceph-client tooling or virtualization build.

## Important APIs, Types, and Functions

Source size: 229 lines, 7902 bytes. Kconfig symbols: INITRAMFS_SOURCE, INITRAMFS_FORCE, INITRAMFS_ROOT_UID, INITRAMFS_ROOT_GID, RD_GZIP, RD_BZIP2, RD_LZMA, RD_XZ, RD_LZO, RD_LZ4, RD_ZSTD, INITRAMFS_COMPRESSION_GZIP, INITRAMFS_COMPRESSION_BZIP2, INITRAMFS_COMPRESSION_LZMA, INITRAMFS_COMPRESSION_XZ, INITRAMFS_COMPRESSION_LZO, INITRAMFS_COMPRESSION_LZ4, INITRAMFS_COMPRESSION_ZSTD, plus 1 more.

## Control Flow and Data Flow

Important local symbols include none; includes are none. Control flow follows the surrounding tool's build or runtime entry points.

## State and Persistence Behavior

State is local to the surrounding tool or kernel subsystem and is not persisted by this file unless generated build outputs are produced.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Risks are mainly integration drift with adjacent headers, build flags, generated files, or kernel ABI expectations.

## Test Signals

Build the owning target and run subsystem smoke tests that exercise this file's exported symbols or generated artifact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/Makefile -->
# sources/distributed-fs/ceph-client/usr/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (obj-$(CONFIG_BLK_DEV_INITRD) :=, hostprogs :=, ramfs-input :=, ramfs-input :=, targets +=) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 85 lines, 2756 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/endian.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/endian.h

## Purpose

`endian.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/limits.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/limits.h

## Purpose

`limits.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (_DUMMY_LIMITS_H, INT_MAX, INT_MIN), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 8 lines, 188 bytes. Macros/defines: _DUMMY_LIMITS_H, INT_MAX, INT_MIN.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/netinet/if_ether.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/netinet/if_ether.h

## Purpose

`if_ether.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include/netinet`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/netinet/if_ether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/netinet/in.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/netinet/in.h

## Purpose

`in.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include/netinet`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/netinet/in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/stddef.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/stddef.h

## Purpose

`stddef.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (_DUMMY_STDDEF_H, offsetof, NULL, NULL), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 13 lines, 260 bytes. Macros/defines: _DUMMY_STDDEF_H, offsetof, NULL, NULL.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/stddef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/stdint.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/stdint.h

## Purpose

`stdint.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/types.h), macros (_DUMMY_STDINT_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 17 lines, 334 bytes. Includes: linux/types.h. Macros/defines: _DUMMY_STDINT_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/stdint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/string.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/string.h

## Purpose

`string.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (stddef.h), macros (_DUMMY_STRING_H, memset, memcpy, strlen), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 12 lines, 307 bytes. Includes: stddef.h. Macros/defines: _DUMMY_STRING_H, memset, memcpy, strlen.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/ioctl.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/sys/ioctl.h

## Purpose

`ioctl.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include/sys`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/socket.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/sys/socket.h

## Purpose

`socket.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/socket.h), macros (_DUMMY_SYS_SOCKET_H), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 12 lines, 301 bytes. Includes: linux/socket.h. Macros/defines: _DUMMY_SYS_SOCKET_H.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include/sys`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/time.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/sys/time.h

## Purpose

`time.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/time.h), macros (none), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 3 lines, 69 bytes. Includes: linux/time.h.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include/sys`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/types.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/sys/types.h

## Purpose

`types.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include/sys`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/sys/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/time.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/time.h

## Purpose

`time.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/unistd.h -->
# sources/distributed-fs/ceph-client/usr/dummy-include/unistd.h

## Purpose

`unistd.h` is an intentionally empty compatibility placeholder in the source tree. Its presence satisfies include paths or build-generated header expectations without adding local declarations.

## Important APIs, Types, and Functions

Source size: 0 lines, 0 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

There is no executable control flow. Build or test sources can include or probe the file and receive an empty translation unit/header contribution.

## State and Persistence Behavior

No runtime or persistent state is stored in the file.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/dummy-include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The main risk is assuming the file is accidental and deleting it; that can break include-path compatibility. It also cannot provide missing definitions if upstream code starts relying on real declarations.

## Test Signals

Build the userspace or host tool targets that place this directory on the include path and verify no include-not-found regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/dummy-include/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_init_cpio.c -->
# sources/distributed-fs/ceph-client/usr/gen_init_cpio.c

## Purpose

Host utility that converts a textual initramfs file list into a `newc` or checksum `crc` cpio archive. It supports regular files, hard links, directories, symlinks, device nodes, pipes, sockets, fixed timestamps, output files, checksums, and best-effort data alignment.

## Important APIs, Types, and Functions

Source size: 781 lines, 17489 bytes. Functions/classes: push_buf, push_pad, push_rest, cpio_trailer, cpio_mkslink, cpio_mkslink_line, if, cpio_mkgeneric, cpio_mkgeneric_line, if, cpio_mkdir_line, cpio_mkpipe_line, cpio_mksock_line, cpio_mknod, cpio_mknod_line, if, cpio_mkfile_csum, cpio_mkfile, plus 32 more. Includes: stdio.h, stdlib.h, stdint.h, stdbool.h, sys/types.h, sys/stat.h, string.h, unistd.h, time.h, fcntl.h, errno.h, ctype.h, limits.h. Macros/defines: _GNU_SOURCE, xstr, str, MIN, CPIO_HDR_LEN, CPIO_TRAILER, padlen, LINE_SIZE.

## Control Flow and Data Flow

Main parses options, opens the list, dispatches each line through `file_handler_table`, writes cpio headers and payloads with `push_*` helpers, and appends a padded `TRAILER!!!`. File entries stat the source, optionally checksum and copy via `copy_file_range` or read/write fallback, and emit hard-link names before the payload-carrying final link.

## State and Persistence Behavior

Persistent output is the archive written to stdout or `-o`. Internal global state tracks archive `offset`, synthetic inode number, timestamp policy, checksum mode, output fd, alignment, and zero padding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Text parsing uses fixed `PATH_MAX` buffers and whitespace-separated fields. Cpio has 32-bit timestamp and file-size limits. Alignment padding is constrained by `PATH_MAX`, and environment expansion writes into the location buffer.

## Test Signals

Generate archives with every record type, hard links, env-expanded paths, checksum mode, fixed timestamps, negative/overflow timestamps, large files, alignment requests, stdin list input, and malformed list lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_init_cpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_initramfs.sh -->
# sources/distributed-fs/ceph-client/usr/gen_initramfs.sh

## Purpose

Shell frontend that turns directories, cpio-list files, or existing cpio archives into the list consumed by `usr/gen_init_cpio`, while also producing dependency lists for kbuild.

## Important APIs, Types, and Functions

Source size: 250 lines, 5922 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Options are processed sequentially so uid/gid/date settings affect following inputs. Directories are traversed with `find`, sorted, converted to `file`, `dir`, `nod`, `slink`, `pipe`, or `sock` entries, and optional deps are emitted. File-list inputs are copied through and scanned for file dependencies, then `usr/gen_init_cpio` is invoked.

## State and Persistence Behavior

Uses a temporary cpio-list removed by trap, plus optional dependency output. Root uid/gid remapping and timestamp options persist across subsequent input arguments until changed.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The script relies on external `find`, `sort`, `sed`, `date`, `ls`, and `readlink`; whitespace in paths is not robustly handled. Direct `.cpio` handling is in the Makefile, not this script.

## Test Signals

Test directory, list-file, multiple input, uid/gid squash and current-user remaps, dependency generation, fixed dates, filenames beginning with `-`, and each file type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_initramfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/include/Makefile -->
# sources/distributed-fs/ceph-client/usr/include/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (always-y :=, clean-files +=) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 188 lines, 6338 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/include/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/include/headers_check.pl -->
# sources/distributed-fs/ceph-client/usr/include/headers_check.pl

## Purpose

`headers_check.pl` is source-tree support code in this subset. It contains 96 lines and contributes to the surrounding Linux/Ceph-client tooling or virtualization build.

## Important APIs, Types, and Functions

Source size: 96 lines, 2068 bytes. Functions/classes: if.

## Control Flow and Data Flow

Important local symbols include if; includes are none. Control flow follows the surrounding tool's build or runtime entry points.

## State and Persistence Behavior

State is local to the surrounding tool or kernel subsystem and is not persisted by this file unless generated build outputs are produced.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr/include`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Risks are mainly integration drift with adjacent headers, build flags, generated files, or kernel ABI expectations.

## Test Signals

Build the owning target and run subsystem smoke tests that exercise this file's exported symbols or generated artifact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/include/headers_check.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/initramfs_data.S -->
# sources/distributed-fs/ceph-client/usr/initramfs_data.S

## Purpose

`initramfs_data.S` embeds the generated initramfs binary blob into the kernel image and exposes its size for early boot code.

## Important APIs, Types, and Functions

Source size: 36 lines, 1243 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Assembler places `.incbin "usr/initramfs_inc_data"` between start/end labels in `.init.ramfs`, then emits `__initramfs_size` in `.init.ramfs.info` as a 32-bit or 64-bit quantity.

## State and Persistence Behavior

Persistent state is the linked initramfs bytes and size symbol in the kernel image. Runtime unpacking is performed by early userspace/initramfs code elsewhere.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Missing generated `initramfs_inc_data`, assembler `.incbin` support, wrong section flags, or size-width mismatch can break boot image construction.

## Test Signals

Build kernels with empty, uncompressed, and compressed initramfs inputs on 32-bit and 64-bit configurations; inspect symbols and boot unpacking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/initramfs_data.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/Makefile -->
# sources/distributed-fs/ceph-client/virt/Makefile

## Purpose

`Makefile` is build glue for the surrounding tool or kernel subtree. It defines targets/variables (obj-y	+=) and wires host tools, test binaries, modules, or generated artifacts into kbuild or standalone make.

## Important APIs, Types, and Functions

Source size: 2 lines, 54 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Make evaluates feature/config variables, selects compiler flags, builds declared targets, includes generated dependency files when present, and provides clean/install or module helper targets where applicable.

## State and Persistence Behavior

Persistent state is build output: objects, binaries, dependency files, generated cpio/header-test files, or modules. The Makefile itself stores build policy, not runtime state.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Relative include paths, host compiler feature detection, generated dependency files, and architecture-specific conditionals are fragile. Cleaning rules must avoid deleting source files while removing generated artifacts.

## Test Signals

Run the relevant `make` targets and `make clean`; for kbuild files, test enabled/disabled config combinations and out-of-tree object directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/Kconfig -->
# sources/distributed-fs/ceph-client/virt/kvm/Kconfig

## Purpose

`Kconfig` is part of the common KVM virtualization core. It contributes configuration, helpers, or implementation used by architecture-specific KVM code.

## Important APIs, Types, and Functions

Source size: 120 lines, 2380 bytes. Kconfig symbols: KVM_COMMON, HAVE_KVM_PFNCACHE, HAVE_KVM_IRQCHIP, HAVE_KVM_IRQ_ROUTING, HAVE_KVM_DIRTY_RING, HAVE_KVM_DIRTY_RING_TSO, HAVE_KVM_DIRTY_RING_ACQ_REL, NEED_KVM_DIRTY_RING_WITH_BITMAP, KVM_MMIO, KVM_ASYNC_PF, KVM_ASYNC_PF_SYNC, HAVE_KVM_MSI, HAVE_KVM_READONLY_MEM, HAVE_KVM_CPU_RELAX_INTERCEPT, KVM_VFIO, HAVE_KVM_INVALID_WAKEUPS, KVM_GENERIC_DIRTYLOG_READ_PROTECT, KVM_GENERIC_PRE_FAULT_MEMORY, plus 14 more.

## Control Flow and Data Flow

Key local functions/types include none. Control flow is driven by KVM ioctls, vCPU entry/exit paths, memory-slot updates, or VM teardown depending on the file.

## State and Persistence Behavior

State is held in `struct kvm`, `struct kvm_vcpu`, per-feature lists/rings/locks, and userspace-visible ABI structures.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

KVM code is concurrency-heavy: SRCU, spinlocks, workqueues, MMU locks, userspace ABI offsets, and teardown ordering are common failure points.

## Test Signals

Use KVM selftests, lockdep/KASAN/KCSAN builds, ioctl negative tests, VM teardown races, and architecture-specific enabled/disabled config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/async_pf.c -->
# sources/distributed-fs/ceph-client/virt/kvm/async_pf.c

## Purpose

Provides common KVM asynchronous page fault support. It queues background work to fault in guest memory and later notifies the vCPU that the page is present or that it should retry synchronously.

## Important APIs, Types, and Functions

Source size: 241 lines, 6335 bytes. Functions/classes: kvm_async_pf_init, kvm_async_pf_deinit, kvm_async_pf_vcpu_init, async_pf_execute, kvm_destroy_vm, kvm_flush_and_free_async_pf_work, kvm_clear_async_pf_completion_queue, kvm_check_async_pf_completion, while, kvm_setup_async_pf, kvm_async_pf_wakeup_all. Includes: linux/kvm_host.h, linux/slab.h, linux/module.h, linux/mmu_context.h, linux/sched/mm.h, async_pf.h, trace/events/kvm.h.

## Control Flow and Data Flow

Setup bounds the per-vCPU queue, rejects error HVAs, allocates a work item, injects arch-specific not-present state, queues work, and increments counters. The work item pins the VM mm if possible, calls `get_user_pages_remote()`, moves itself to the done list, notifies/kicks the vCPU, and completion dequeue runs arch ready/present hooks before freeing.

## State and Persistence Behavior

Each vCPU owns async PF queue/done lists, lock, and queued count. A global kmem cache stores `struct kvm_async_pf` work items. Wake-all entries skip normal work execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Lifetime spans workqueue execution, VM teardown, module unload, and vCPU completion. Queue entries must be flushed even when already done. `CONFIG_KVM_ASYNC_PF_SYNC` changes present-notification ordering.

## Test Signals

Exercise successful async faults, GUP failure, queue-full fallback, VM teardown with queued/done work, wake-all, sync and async configs, and arch dequeue blocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/async_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/async_pf.h -->
# sources/distributed-fs/ceph-client/virt/kvm/async_pf.h

## Purpose

`async_pf.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (__KVM_ASYNC_PF_H__, kvm_async_pf_init, kvm_async_pf_deinit, kvm_async_pf_vcpu_init), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 24 lines, 518 bytes. Macros/defines: __KVM_ASYNC_PF_H__, kvm_async_pf_init, kvm_async_pf_deinit, kvm_async_pf_vcpu_init.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/async_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/binary_stats.c -->
# sources/distributed-fs/ceph-client/virt/kvm/binary_stats.c

## Purpose

Common reader for KVM binary stats file descriptors. It exposes a contiguous virtual file layout containing header, id string, descriptor array, and raw stats data.

## Important APIs, Types, and Functions

Source size: 144 lines, 4604 bytes. Functions/classes: kvm_stats_read. Includes: linux/kvm_host.h, linux/kvm.h, linux/errno.h, linux/uaccess.h.

## Control Flow and Data Flow

`kvm_stats_read()` computes the available length from the current offset, then conditionally copies each region in order with offset-aware slicing and advances the file offset.

## State and Persistence Behavior

The function does not own stats storage; it reads caller-provided id/header/descriptors/data. Persistent state is the userspace fd offset and the underlying KVM stats memory.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Offset math must not overrun the descriptor or data regions. A partial `copy_to_user()` returns `-EFAULT` after prior bytes may have been copied. Header offsets must match the actual layout.

## Test Signals

pread/read header-only, id-only, descriptor-only, data-only, unaligned cross-boundary reads, EOF reads, and injected user-copy faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/binary_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.c -->
# sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.c

## Purpose

Implements KVM coalesced MMIO/PIO zones, letting repeated guest writes be queued into a shared ring for userspace to drain instead of exiting on every write.

## Important APIs, Types, and Functions

Source size: 190 lines, 4708 bytes. Functions/classes: Copyright, coalesced_mmio_in_range, coalesced_mmio_write, coalesced_mmio_destructor, kvm_coalesced_mmio_init, kvm_coalesced_mmio_free, kvm_vm_ioctl_register_coalesced_mmio, kvm_vm_ioctl_unregister_coalesced_mmio, list_for_each_entry_safe. Includes: kvm/iodev.h, linux/kvm_host.h, linux/slab.h, linux/kvm.h, coalesced_mmio.h.

## Control Flow and Data Flow

Registration creates an IO device for a zone and adds it to the MMIO or PIO bus under `slots_lock`. Writes validate range, lock the shared ring, check userspace-controlled indices and capacity, copy address/data/pio fields, publish with `smp_wmb()`, and advance `last`. Unregistration removes matching zones.

## State and Persistence Behavior

VM state includes a zeroed page-backed coalesced ring, `ring_lock`, and `coalesced_zones` list. Devices persist until unregistered or destroyed by the IO bus.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Userspace controls `first` and can make the ring appear full or corrupt indices; kernel defends by checking bounds. Range overflow, pio flag validation, and destructor/list lifetime are important.

## Test Signals

Register/unregister MMIO and PIO zones, write in/out of range, fill ring to full, mutate first/last from userspace, and verify ordering of data before index publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.h -->
# sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.h

## Purpose

`coalesced_mmio.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (linux/list.h), macros (__KVM_COALESCED_MMIO_H__), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 39 lines, 884 bytes. Functions/classes: kvm_coalesced_mmio_init, kvm_coalesced_mmio_free. Includes: linux/list.h. Macros/defines: __KVM_COALESCED_MMIO_H__.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/dirty_ring.c -->
# sources/distributed-fs/ceph-client/virt/kvm/dirty_ring.c

## Purpose

Implements common KVM dirty-ring tracking, where vCPU threads append dirtied GFNs to a ring and userspace harvests and resets entries for migration/logging.

## Important APIs, Types, and Functions

Source size: 272 lines, 7344 bytes. Functions/classes: kvm_cpu_dirty_log_size, kvm_dirty_ring_get_rsvd_entries, kvm_use_dirty_bitmap, kvm_arch_allow_write_without_running_vcpu, kvm_dirty_ring_used, kvm_dirty_ring_soft_full, kvm_dirty_ring_full, kvm_reset_dirty_gfn, kvm_dirty_ring_alloc, kvm_dirty_gfn_set_invalid, kvm_dirty_gfn_set_dirtied, kvm_dirty_gfn_harvested, kvm_dirty_ring_reset, while, if, if, if, if, plus 3 more. Includes: linux/kvm_host.h, linux/kvm.h, linux/vmalloc.h, linux/kvm_dirty_ring.h, trace/events/kvm.h, kvm_mm.h.

## Control Flow and Data Flow

Allocation vzallocs a ring and computes the soft limit. `kvm_dirty_ring_push()` writes slot/offset, publishes dirty flags with ordering, advances `dirty_index`, and requests a soft-full exit. `kvm_dirty_ring_reset()` scans harvested entries, invalidates them, batches nearby GFNs per memslot into bitmasks, and re-enables dirty logging in the MMU.

## State and Persistence Behavior

Per-ring state includes `dirty_gfns`, size, soft limit, dirty/reset indices, and vCPU ring index. Userspace observes flags and marks entries reset; kernel reset runs under `slots_lock`.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Reset batching must handle forward/backward offsets without overflow. Ring-full conditions should be prevented by soft limits and reserved entries. Memory ordering on flags is the userspace ABI.

## Test Signals

Test wraparound, soft-full exits, reset batching in one slot and across slots, invalid slot/offset handling, signal interruption, bitmap fallback modes, and userspace harvest/reset ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/dirty_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/eventfd.c -->
# sources/distributed-fs/ceph-client/virt/kvm/eventfd.c

## Purpose

Implements KVM eventfd integration: irqfd maps eventfd signals to guest interrupts, resamplefd handles level-triggered deassert notifications, and ioeventfd maps guest MMIO/PIO writes to eventfd signals.

## Important APIs, Types, and Functions

Source size: 1052 lines, 26272 bytes. Functions/classes: __attribute__, irqfd_inject, if, irqfd_resampler_notify, irqfd_resampler_ack, irqfd_resampler_shutdown, if, irqfd_shutdown, if, irqfd_is_active, irqfd_deactivate, __attribute__, irqfd_wakeup, if, if, irqfd_update, kvm_irqfd_register, __attribute__, plus 36 more. Includes: linux/kvm_host.h, linux/kvm.h, linux/kvm_irqfd.h, linux/workqueue.h, linux/syscalls.h, linux/wait.h, linux/poll.h, linux/file.h, linux/list.h, linux/eventfd.h, linux/kernel.h, linux/srcu.h, linux/slab.h, linux/seqlock.h, linux/irqbypass.h, trace/events/kvm.h, kvm/iodev.h.

## Control Flow and Data Flow

irqfd assignment validates architecture state, grabs eventfd contexts, optionally attaches a resampler, registers a priority waitqueue callback through `vfs_poll`, injects pending events, and supports IRQ bypass. Wakeups read eventfd counts, try in-atomic IRQ injection using current routing, and defer to work if needed. Deassign/release deactivate entries and flush cleanup. ioeventfd assignment validates flags/lengths, checks collisions, registers an IO device, and signals eventfd from its write callback.

## State and Persistence Behavior

KVM holds `irqfds.items`, `resampler_list`, `ioeventfds`, seqcount-protected routing entries, eventfd refs, waitqueue entries, work items, and per-bus ioeventfd counts. SRCU, spinlocks, mutexes, and a cleanup workqueue serialize lifetime and routing updates.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Ordering is delicate around eventfd waitqueue registration, EPOLLHUP, SRCU routing updates, resampler list removal, and IRQ bypass. ioeventfd collision matching must avoid duplicate wildcard/datamatch registrations. Cleanup must flush deferred injection before freeing objects.

## Test Signals

KVM selftests should cover irqfd assign/deassign, eventfd close while active, pending event at registration, resamplefd ack, routing updates, IRQ bypass transitions, ioeventfd MMIO/PIO/datamatch/wildcard/fast-MMIO paths, and invalid flag/length cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/eventfd.c -->
