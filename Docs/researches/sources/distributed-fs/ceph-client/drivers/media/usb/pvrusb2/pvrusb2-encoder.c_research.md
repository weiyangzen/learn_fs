<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.c

Purpose: CX23416 MPEG encoder mailbox support for pvrusb2. It sends memory read/write requests through the FX2 firmware, wraps cx2341x control updates, and starts/stops/configures MPEG/VBI capture.

Important APIs/types/functions: `pvr2_encoder_write_words()` and `pvr2_encoder_read_words()` access encoder mailbox/memory through FX2 commands. `pvr2_encoder_cmd()` implements the cx2341x mailbox callback. `pvr2_encoder_vcmd()` is a vararg helper. `pvr2_encoder_prep_config()` sends hardware-specific `CX2341X_ENC_MISC` setup. Public functions are `pvr2_encoder_adjust()`, `pvr2_encoder_configure()`, `pvr2_encoder_start()`, and `pvr2_encoder_stop()`.

Control flow: configuration sets cx2341x port, width, height, 50/60 Hz state, sends prep commands, programs vsync/event/VBI settings, applies cx2341x control state, then initializes input. The mailbox command path writes command words with driver flags clear, writes a busy/done flag, polls for firmware done, copies return args, and clears the mailbox. Start unmasks interrupts, optionally mutes video for radio input, and sends `START_CAPTURE` with MPEG or VBI parameters. Stop masks interrupts and sends `STOP_CAPTURE`.

State and persistence: encoder state is tracked in `struct pvr2_hdw`: command buffer, encoder health/run flags, current/control cx2341x state, active stream type, resolution, standard mask, timers, and locks. Hardware mailbox and encoder firmware state persist until reset/reload.

Dependencies and integration: depends on Linux firmware/cx2341x controls, pvrusb2 hardware internals, FX2 command constants, utility endian macros, and trace flags. The cx2341x module calls back into `pvr2_encoder_cmd()` through `cx2341x_update()`.

Risks: mailbox polling has retry and timeout heuristics; repeated failures mark encoder state bad and rely on firmware reload/reinitialization. Read/write chunk formats are limited by FX2 firmware and must stay in sync. Some `ENC_MISC` commands are reverse-engineered and comments document harmful variants. `pvr2_encoder_vcmd()` uses varargs with `u32` expectations; callers must pass correct types.

Test signals: encoder firmware load/configure; V4L2 MPEG control updates; start/stop MPEG and VBI streams; channel change/no-signal recovery without video corruption; forced mailbox timeout; trace encoder commands and state-bit changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.c -->
