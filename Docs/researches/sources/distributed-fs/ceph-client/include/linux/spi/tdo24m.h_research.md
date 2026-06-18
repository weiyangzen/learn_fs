<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/tdo24m.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/tdo24m.h

Purpose: This header defines platform data for TDO24M/TDO35S SPI display panels.

Important APIs/types/functions: `enum tdo24m_model` identifies `TDO24M` and `TDO35S`; `tdo24m_platform_data` stores the selected model.

Control flow: Board code provides the model; the display driver uses it during probe to select initialization and timing behavior.

State and persistence: Static board description only. Panel power, mode, and framebuffer state are driver-owned.

Dependencies/integration: Integrates with SPI display/panel driver setup.

Risks and test signals: Risks include wrong model selection causing invalid panel init. Test panel probe, mode timing, color output, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/tdo24m.h -->
