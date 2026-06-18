<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/bpf-lirc.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/bpf-lirc.c

Purpose: eBPF integration for LIRC mode2/raw IR devices. It lets users attach BPF programs to raw IR samples and use helper calls to emit rc-core key, repeat, or relative-pointer events.

Important APIs and functions: exports `lirc_mode2_prog_ops` and `lirc_mode2_verifier_ops`. BPF helpers are `bpf_rc_repeat`, `bpf_rc_keydown`, and `bpf_rc_pointer_rel`, with prototypes selected by `lirc_mode2_func_proto`. Attachment lifecycle uses `lirc_prog_attach`, `lirc_prog_detach`, `lirc_prog_query`, `lirc_bpf_attach`, `lirc_bpf_detach`, `lirc_bpf_run`, and `lirc_bpf_free`.

Control flow: verifier access permits only a single read-only `u32` context sample. Attach obtains an `rc_dev` from a target fd, requires `RC_DRIVER_IR_RAW`, locks `ir_raw_handler_lock`, copies the old BPF program array with the new program appended, swaps it with RCU, and frees the old array. Detach performs the inverse and drops program references. Raw IR receive code calls `lirc_bpf_run`, which stores the sample in `ir_raw_event_ctrl` and runs the RCU-protected program array. Query returns attach flags and program IDs to userspace.

State and persistence: BPF program arrays live under `rcdev->raw->progs` and are RCU-managed. `raw->bpf_sample` is the per-run context value. Program references persist until detach or `lirc_bpf_free`, which must run after the rc thread is stopped and under the raw handler lock.

Dependencies and integration points: depends on Linux BPF/filter APIs, `linux/bpf_lirc.h`, rc-core private raw handler state, input relative events, rc key helpers, and RCU. Kconfig requires built-in rc-core for BPF LIRC support.

Risks: maximum attached programs is fixed at 64. Attach/detach correctness depends on `ir_raw_handler_lock` and RCU lifetime ordering. Helpers can emit input/rc events from BPF program logic, so verifier restrictions and helper availability are the main safety boundary. `trace_printk` is exposed only with token `CAP_PERFMON`.

Test signals: BPF attach/detach/query via `bpf(2)`, verifier rejection of invalid context access, multiple program ordering, raw IR sample processing, helper-generated key/repeat/pointer events, and teardown after rc device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/bpf-lirc.c -->
