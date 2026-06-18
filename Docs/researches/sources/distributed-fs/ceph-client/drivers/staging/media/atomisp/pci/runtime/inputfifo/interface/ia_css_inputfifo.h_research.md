# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/interface/ia_css_inputfifo.h

Purpose: declares the host/simulator path that pushes synthetic input frames and lines into the streaming-to-MIPI input FIFO.

Important APIs: full-frame send (`ia_css_inputfifo_send_input_frame`), streaming lifecycle (`start_frame`, `send_line`, `send_embedded_line`, `end_frame`). Parameters include MIPI channel id, stream format, optional two-PPC, line data pointers, and widths.

Control flow/state: callers can either send a whole frame in one call or manually bracket lines between start/end. Implementation tracks per-channel streaming state in static channel administration.

Dependencies/integration: includes SP/ISP headers and `ia_css_stream_format.h`; implementation depends on event FIFO, input system format conversion, and streaming-to-MIPI token definitions.

Risks: `ch_id` indexes a fixed four-entry table in implementation without header-level bounds. Data is raw `unsigned short` words and must already match format-specific packing assumptions.

Test signals: whole-frame RAW/YUV/RGB sends, manual embedded-line insertion, invalid channel bounds, two-PPC odd widths, and token stream inspection in simulator.
