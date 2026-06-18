# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp_gen_header.h

Purpose: generic MCP firmware header definitions used to validate loaded or running Myri-10G firmware and discover optional runtime metadata.

Important declarations: `MCP_HEADER_PTR_OFFSET`, MCP type constants (`MCP_TYPE_ETH`, `MCP_TYPE_PCIE`, etc.), `struct mcp_gen_header`, and `struct zmcp_info`. The header includes fixed leading fields and extension fields guarded by `header_length`.

Control flow: no executable flow. `myri10ge_load_hotplug_firmware`, `myri10ge_adopt_running_firmware`, and LED identification code read these structures from firmware image or NIC SRAM.

State and persistence: represents firmware image metadata and runtime SRAM metadata, including version string, SRAM size, string specs, MCP index, features, EEPROM header address, and LED patterns.

Dependencies and integration: included by `myri10ge.c`; relies on callers to swab/ntohl fields according to source location.

Risks: callers must check `header_length` before using extension fields. Incorrect header offset or type validation could load non-Ethernet firmware. LED support detection depends on `led_pattern` being within the advertised header length.

Test signals: firmware image validation with good/bad header offsets and types, adopted firmware validation, and ethtool physical ID LED behavior on firmware with and without LED fields.
