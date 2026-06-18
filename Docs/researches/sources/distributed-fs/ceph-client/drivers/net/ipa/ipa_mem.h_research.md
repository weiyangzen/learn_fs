# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.h

Purpose: defines IPA local memory region IDs, memory-region descriptors, constraints, and public memory lifecycle/setup APIs.

Important APIs/types: `enum ipa_mem_id` lists all IPA-resident regions for UC shared/info, v4/v6 filter and route tables, modem/AP header and processing contexts, modem scratch, UC event ring, PDN config, statistics, AP filter tables, NAT table, and an end-marker pseudo-region. `struct ipa_mem` stores region ID, offset, size, and canary count. `IPA_MEM_MAX` limits individual region zero-buffer handling.

Control flow: exported functions split responsibilities: `ipa_mem_init/exit()` map resources and persistent external memory; `ipa_mem_config/deconfig()` validate hardware shared memory and allocate/free zero DMA buffer; `ipa_mem_setup()` issues one-time immediate-command initialization; `ipa_mem_zero_modem()` is called during modem crash recovery.

State/persistence: the header documents constraints that data tables must satisfy: offsets are relative to the IPA shared memory base, region sizes exclude canaries, offsets point after canaries, most regions are 8-byte aligned/sized, modem memory is 4-byte sized, and UC event ring is 1024-byte aligned.

Dependencies/integration: forward-declares `struct ipa`, `struct platform_device`, and `struct ipa_mem_data`; implementation interacts with `ipa_data`, IPA tables, QMI, and immediate commands.

Risks: region IDs are cross-file contracts used by memory setup, table setup, QMI messages, and SSR zeroing. Reordering or adding IDs requires synchronized data tables and version validation.

Test signals: all configured `ipa_mem_data` entries use valid IDs and alignments, required IDs are present for the IPA version, and modem/QMI boot succeeds with advertised memory windows.
