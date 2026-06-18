# sources/distributed-fs/ceph-client/sound/drivers/vx/vx_cmd.h

Purpose: declares logical DSP command IDs, opcode masks, notification constants, delayed-command flags, audio/pipe bit masks, time-code constants, and inline helpers for constructing VX RMH command words.

Important APIs, types, and functions: the central enum runs from `CMD_VERSION` to `CMD_LAST_INDEX` and must match `vx_dsp_cmds[]` in `vx_cmd.c`. `struct vx_cmd_info` describes command metadata. `vx_init_rmh()` is declared for table-based RMH initialization. `vx_set_pipe_cmd_params()` and `vx_set_stream_cmd_params()` inline common command-word packing for capture/playback, pipe index, stream index, and secondary parameters.

Control flow: all VX subsystem files include this header to build DSP requests. Callers first initialize the RMH, then use masks such as `COMMAND_RECORD_MASK`, `MASK_FIRST_FIELD`, `FIELD_SIZE`, and `MASK_DSP_WORD` to pack capture and routing data before `vx_send_msg()`.

State and persistence: none. The file defines protocol constants that must remain stable with the DSP firmware.

Dependencies and integration: integrated with `sound/vx_core.h` for `struct vx_rmh` and hardware definitions, with `vx_cmd.c` for command metadata, and with PCM/mixer/UER code that interprets notification and delayed-command bitfields.

Risks: this header encodes a binary DSP protocol, so small mask/shift errors affect many runtime paths. Comments use C++-style `//` in a kernel C header, which is accepted in modern builds but should be consistent with tree style. Inline helpers intentionally OR into `rmh->Cmd[0]`; callers must initialize RMH first and avoid stale bits. Test signals are compile coverage, command packing unit checks for playback/capture pipe values, and integration tests that exercise stream start, format, audio level, clock, and notification commands.
