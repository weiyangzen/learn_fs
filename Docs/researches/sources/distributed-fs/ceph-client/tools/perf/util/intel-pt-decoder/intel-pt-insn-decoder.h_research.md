# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.h

Purpose: declares the instruction classification surface used by Intel PT and BTS code.

Important APIs and types: defines `INTEL_PT_INSN_DESC_MAX`, `INTEL_PT_INSN_BUF_SZ`, `enum intel_pt_insn_op`, `enum intel_pt_insn_branch`, and `struct intel_pt_insn` with operation, branch class, emulated PTWRITE flag, length, relative displacement, and copied bytes. Declares decode, name, description, and perf-flag conversion functions.

Control flow: consumers call `intel_pt_get_insn()` with raw x86 bytes and execution mode, then inspect `op`, `branch`, `length`, and `rel`. Formatting helpers are for logs/UI; `intel_pt_insn_type()` feeds perf sample flags.

State and persistence: no persistent state. The copied instruction buffer in `struct intel_pt_insn` lets later sample/log code retain bytes after the source memory is gone.

Dependencies and integration: includes standard size/int headers; implementations integrate with the x86 instruction decoder and perf sample flags.

Risks: buffer size is fixed at 16 bytes, matching x86 maximum instruction length; changing it affects sample storage assumptions. `bool` is used without including `<stdbool.h>` here, so this header relies on transitive includes in current build contexts.

Test signals: standalone include/build checks, decode fixtures, and consumers verifying the instruction buffer remains valid in synthesized events.
