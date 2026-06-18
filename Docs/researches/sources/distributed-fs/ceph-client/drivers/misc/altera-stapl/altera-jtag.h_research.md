# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-jtag.h

Purpose: defines the Altera STAPL JTAG state structures and declares the TAP manipulation functions implemented in `altera-jtag.c`.

Important APIs and types: `enum altera_jtag_state` names the full TAP state set plus `ILLEGAL_JTAG_STATE`. `struct altera_jtag` stores current state, DR/IR stop states, pre/post counts, buffer lengths, and owned buffers. `struct altera_state` combines an `altera_config`, JTAG state, message buffer, and fixed-size interpreter stack. The header declares scan, swap, wait, pre/post, and cleanup helpers.

Control flow: `altera.c` creates `struct altera_state`, initializes it with `altera_jinit`, and then uses these functions while interpreting bytecode opcodes such as DRSCAN, IRSCAN, WAIT, DRPRE, DRPOST, IRPRE, and IRPOST.

State and persistence: state is per firmware execution. The `stack` and `msg_buff` are part of interpreter state, while the nested `struct altera_jtag` persists scan configuration across opcodes until `altera_free_buffers`.

Dependencies and integration points: requires `struct altera_config` from `<misc/altera.h>` and kernel integer types. It is the internal contract between the bytecode interpreter and the JTAG transport implementation.

Risks: `ALTERA_STACK_SIZE` is fixed at 128, so bytecode stack-depth handling depends on runtime checks. The header exposes raw buffers and counts without encapsulation, making ownership discipline important. Invalid enum values can be passed to stop-state setters without local validation.

Test signals: build coverage, interpreter tests that stress stack depth and scan padding, and assertions that cleanup releases all buffers after failed and successful firmware executions.
