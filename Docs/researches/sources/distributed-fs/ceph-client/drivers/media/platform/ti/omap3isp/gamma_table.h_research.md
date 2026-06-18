# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/gamma_table.h


Purpose: Provides the default gamma lookup table data used by the OMAP3 ISP preview engine for all color components. Like the CFA table, it is an include fragment containing initializer values.

Important APIs/types: The file is a monotonically nondecreasing sequence of 8-bit output values from 0 to 255, heavily repeated in high ranges, representing a default gamma curve.

Control flow: No executable logic. The including preview code embeds the values into a gamma table and writes them into ISP preview hardware or keeps them as default configuration data.

State and persistence: Read-only compile-time lookup data.

Dependencies/integration: Used by the OMAP3 ISP preview module. Its length and value range must match the hardware gamma table size and the structure initializer in the includer.

Risks and test signals: Raw initializer fragments are easy to break by adding guards or declarations that the includer does not expect. Image pipeline tests should validate default preview output, table upload, and no out-of-bounds reads/writes when the preview module indexes the table.
