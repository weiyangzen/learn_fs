# sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,exynos-usi.h

Source read summary: 27 lines, 707 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,exynos-usi.h` declares device-tree constants for the Samsung Exynos SoC binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 11 visible constants or packing macros; representative names are `USI_MODE_NONE`, `USI_MODE_UART`, `USI_MODE_SPI`, `USI_MODE_I2C`, `USI_MODE_I2C1`, `USI_MODE_I2C0_1`, `USI_MODE_UART_I2C1`, `USI_V2_NONE`, `USI_V2_UART`, `USI_V2_SPI`, `USI_V2_I2C`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
