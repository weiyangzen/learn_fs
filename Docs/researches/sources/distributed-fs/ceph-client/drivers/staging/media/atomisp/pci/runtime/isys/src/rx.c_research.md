# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/rx.c

Purpose: configures CSS receiver hardware, maps MIPI/AtomISP formats, translates/clears RX interrupts, and calculates input-system alignment/compression settings.

Important functions: `ia_css_isys_rx_enable_all_interrupts`, port conversion, IRQ get/clear/translate helpers, format mapping for ISP2400/2401, `ia_css_isys_convert_stream_format_to_mipi_format`, compression conversion, `ia_css_csi2_calculate_input_system_alignment`, `ia_css_isys_rx_configure`, and `ia_css_isys_rx_disable`.

Control flow: IRQ functions read receiver status registers and map hardware bits to `IA_CSS_RX_IRQ_INFO_*`. Format conversion selects compressed raw custom types or platform-specific MIPI constants. RX configure disables the selected port, writes timeout/count registers and GPREG routing, optionally updates global two-PPC registers if no port was already enabled, then re-enables the port.

State/persistence: writes receiver port/global registers and input-system GPREGs. No owned heap state.

Dependencies/integration: inline `input_system.h` receiver accessors, CSS IRQ enable, stream formats, compression structs, and `sh_css_internal` flags.

Risks: comments identify multi-stream hazards around shared two-PPC and GPREG mux/multicast programming. `ia_css_isys_rx_clear_irq_info` reads/writes the IRQ enable register while named as clearing status, requiring hardware-specific validation.

Test signals: IRQ bit translation for every bit, all supported input format mappings on ISP2400/2401, compression mapping invalid cases, lane table per RX mode/port, buffered vs non-buffered GPREG routing, and multi-stream receiver configuration.
