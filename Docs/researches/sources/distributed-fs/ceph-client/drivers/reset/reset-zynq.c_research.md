# sources/distributed-fs/ceph-client/drivers/reset/reset-zynq.c

Purpose: Xilinx Zynq reset controller using the SLCR syscon regmap and a memory resource that describes reset register offset/count.

Important APIs/types/functions: `zynq_reset_data` stores SLCR regmap, rcdev, and base offset. Assert/deassert/status compute bank and bit from reset ID and use `regmap_update_bits()` or `regmap_read()`. Probe obtains the `syscon` phandle and first memory resource, then registers `resource_size / 4 * BITS_PER_LONG` resets.

Control flow: built-in platform driver binds `xlnx,zynq-reset`; consumers index reset bits across banks relative to resource start.

State and persistence: SLCR hardware bits persist; driver state is devm allocated.

Dependencies and integration: syscon phandle, platform resources, regmap, built-in reset provider, OF bindings.

Risks and test signals: `BITS_PER_LONG` makes reset count and bank division architecture-width dependent, while registers are 32-bit. Deassert writes `~BIT(offset)` as value under mask, which relies on mask handling. Test on 32- and 64-bit builds, resource size, syscon lookup failures, and status polarity.
