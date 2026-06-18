# sources/distributed-fs/ceph-client/drivers/nvmem/microchip-otpc.c

Purpose: Read-only NVMEM provider for Microchip SAMA7G5 OTPC packetized OTP memory.

Important APIs/types/functions: `struct mchp_otpc` owns MMIO base, device, packet list, and packet count. `struct mchp_otpc_packet` maps logical packet IDs to hardware word offsets. `mchp_otpc_init_packets_list()` scans headers to build the packet table; `mchp_otpc_read()` translates NVMEM offsets to packet IDs and reads headers/payloads through `mchp_otpc_prepare_read()`.

Control flow: probe maps the controller, scans packets until a zero payload size or the maximum memory size is reached, sets the NVMEM size to accumulated packet bytes, and registers read-only 4-byte stride access. Runtime reads divide the NVMEM offset by four to identify a packet, trigger controller reads for each packet, copy header then payload words, and continue until the requested byte count is filled.

State/persistence: OTP contents persist in hardware. The packet list is devm-allocated at probe and forms the stable logical index for NVMEM consumers.

Dependencies/integration: platform driver for `microchip,sama7g5-otpc`; uses bitfield helpers, MMIO polling, NVMEM provider, and legacy fixed OF cells.

Risks: the NVMEM address space is packet-ID oriented, not a raw physical byte map, so consumers must understand the packet layout. Payload loop uses the header's size field and must trust hardware to avoid malformed packet sequences; probe bounds scanning by `MCHP_OTPC_SIZE`.

Test signals: packet-list construction from multiple payload sizes, invalid packet IDs returning `-EINVAL`, controller read timeout, and cell reads that include header and payload words.
