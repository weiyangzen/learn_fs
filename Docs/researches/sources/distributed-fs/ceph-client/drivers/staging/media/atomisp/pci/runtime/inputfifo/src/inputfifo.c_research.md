# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/src/inputfifo.c

Purpose: implements streaming-to-MIPI token generation for simulated/manual input frames.

Important functions/state: static token helpers (`inputfifo_send_data_a/b`, `inputfifo_send_sol/eol/sof/eof`, `inputfifo_send_line2`, `inputfifo_send_frame`), format classification (`inputfifo_determine_type`), and public frame/line APIs. Static globals hold current channel/format and per-channel `inputfifo_instance` records for four virtual channels.

Control flow: format conversion uses `ia_css_isys_convert_stream_format_to_mipi_format`. Start emits channel/format and SOF tokens. Each line emits blanking, SOL, marker tokens, pixel tokens to A/B lanes according to two-PPC and RGB/YUV420 legacy rules, trailing blanking, and EOL. End emits marker tokens and EOF.

State/persistence: per-channel admin persists across manual start/send/end. `_sh_css_fifo_snd` busy-waits until the event FIFO can accept a token.

Dependencies/integration: event FIFO, SP/ISP/IRQ inline accessors, input system MIPI format conversion, HIVE streaming-to-MIPI token bit definitions, and CSS input mode simulation.

Risks: fixed channel array has no explicit bounds guard. Busy-waiting can hang if event FIFO stops accepting tokens. RGB/YUV legacy two-PPC packing assumes callers inserted data in exact expected order.

Test signals: token traces for RAW/YUV420/YUV420 legacy/RGB, odd line widths, embedded metadata lines, full-frame vs manual API equivalence, and FIFO-full retry behavior.
