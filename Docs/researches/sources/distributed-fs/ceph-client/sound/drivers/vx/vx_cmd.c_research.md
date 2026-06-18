# sources/distributed-fs/ceph-client/sound/drivers/vx/vx_cmd.c

Purpose: maps logical VX DSP command identifiers to 24-bit DSP opcodes, command lengths, and expected status formats. It is the lookup table used by all RMH command construction.

Important APIs, types, and functions: `vx_dsp_cmds[]` is indexed by the enum in `vx_cmd.h` and stores `struct vx_cmd_info` entries: opcode, command length, status sizing mode, and fixed status length. `vx_init_rmh()` initializes a `struct vx_rmh` by copying those fields and setting the first command word.

Control flow: callers throughout VX core, PCM, mixer, and UER code call `vx_init_rmh(&rmh, CMD_...)`, then append pipe/stream/audio parameters before sending with `vx_send_msg()`. The table covers versioning, interrupt tests, pipe allocation/configuration, stream format/control, audio level/metering, clock, time code, monitoring, and end-of-buffer notification commands.

State and persistence: the table is static const command metadata. `vx_init_rmh()` mutates only the caller-provided RMH. There is no persistent or runtime global state.

Dependencies and integration: tightly coupled to `vx_cmd.h` enum ordering and DSP firmware protocol. It depends on `RMH_SSIZE_*` status conventions from VX core headers and on all users respecting command lengths before adding extra words.

Risks: any enum/table mismatch silently creates wrong DSP opcodes. Some command lengths are zero or variable-like for legacy effect commands, so users must validate before indexing. `vx_init_rmh()` uses `snd_BUG_ON(cmd >= CMD_LAST_INDEX)` but otherwise returns without clearing RMH on invalid input. Test signals include command table size coverage through `CMD_LAST_INDEX`, known opcode validation for representative commands, and smoke tests for every caller path that builds command parameters.
