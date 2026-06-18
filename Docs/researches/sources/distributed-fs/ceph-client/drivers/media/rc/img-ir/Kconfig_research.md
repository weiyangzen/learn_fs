<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Kconfig

Purpose: Kconfig options for the Imagination Technologies IR decoder block, selecting raw mode, hardware decode mode, and per-protocol hardware decoders.

Important APIs and symbols: `IR_IMG` is the main tristate and depends on `RC_CORE` plus MIPS or compile-test. `IR_IMG_RAW` enables raw edge reporting. `IR_IMG_HW` enables hardware decode and is selected by default when raw mode is not enabled. Protocol booleans `IR_IMG_NEC`, `IR_IMG_JVC`, `IR_IMG_SONY`, `IR_IMG_SHARP`, `IR_IMG_SANYO`, `IR_IMG_RC5`, and `IR_IMG_RC6` depend on hardware decode, with NEC selecting `BITREVERSE`.

Control flow: selected symbols determine which objects the img-ir Makefile links into the aggregate `img-ir.o` module and which decode modes/protocols are available to runtime setup.

State and persistence: no runtime state. Configuration persists in the kernel build config.

Dependencies and integration points: sourced from the rc device menu. Integrates ImgTec platform hardware with rc-core raw decoders or hardware scancode decode support.

Risks: enabling only raw mode trades reliability and CPU use for protocol flexibility, as documented in help text. Hardware RC6 support is limited to mode 0. Protocol booleans do nothing without `IR_IMG_HW`.

Test signals: Kconfig matrix builds for raw-only, hardware-only, and protocol combinations; module contents matching enabled protocols; device-tree probe on compatible hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Kconfig -->
