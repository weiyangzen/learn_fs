# sources/distributed-fs/ceph-client/drivers/mfd/mcp-sa11x0.c

Purpose: SA11x0 platform host driver for the MCP bus. It maps SA11x0 MCP registers, implements low-level MCP ops, initializes divisors and timeouts, and publishes an MCP host for an attached codec/peripheral.

Important APIs, types, and functions: `struct mcp_sa11x0` stores two mapped register bases and cached `MCCR0/MCCR1`. Ops include `mcp_sa11x0_set_telecom_divisor()`, `mcp_sa11x0_set_audio_divisor()`, `mcp_sa11x0_write()`, `mcp_sa11x0_read()`, `mcp_sa11x0_enable()`, and `mcp_sa11x0_disable()`. `mcp_sa11x0_probe()` requests memory regions, allocates an MCP host, maps IO, initializes hardware, computes `rw_timeout`, and calls `mcp_host_add()`. PM callbacks save/restore by disabling and rewriting cached control registers.

Control flow: platform probe validates board data and resources, claims both register ranges, allocates the host with private data, maps IO, writes initial control state, and registers the MCP device. Read/write ops busy-wait for completion bits after issuing register transactions. Remove unregisters the MCP host, unmaps IO, frees host memory, and releases regions.

State and persistence: cached control registers in `struct mcp_sa11x0` are the authoritative software view for divisor and enable state. Hardware register writes persist until suspend/remove or another writer changes them. The MCP core tracks host use count.

Dependencies and integration points: depends on SA11x0 machine headers, platform data `mcp_plat_data`, the generic MCP core, platform resources, and PM sleep hooks.

Risks: manual resource management has many failure labels and depends on both mappings being present before cleanup. Read/write timeout paths log warnings but still return an unsigned value, with read returning a negative error cast to unsigned. Probe uses legacy `ioremap()` and `request_mem_region()` rather than devm helpers. Test signals include resource failure injection, timeout behavior, suspend/resume while enabled, divisor programming, and codec platform-data propagation.
