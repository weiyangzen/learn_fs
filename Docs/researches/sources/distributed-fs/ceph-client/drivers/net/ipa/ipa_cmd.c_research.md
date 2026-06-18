# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_cmd.c

Purpose: Implements IPA immediate-command construction and validation. Immediate commands use the AP command TX GSI endpoint to initialize tables/headers, write registers, DMA to/from IPA memory, clear the pipeline, and tag status.

Important APIs/functions: Public functions include `ipa_cmd_table_init_valid()`, command pool init/exit, `ipa_cmd_table_init_add()`, `ipa_cmd_hdr_init_local_add()`, `ipa_cmd_register_write_add()`, `ipa_cmd_dma_shared_mem_add()`, `ipa_cmd_pipeline_clear_add()`, `ipa_cmd_pipeline_clear_count()`, `ipa_cmd_pipeline_clear_wait()`, `ipa_cmd_trans_alloc()`, and `ipa_cmd_init()`. Internal helpers validate header/register-write fields, allocate DMA-coherent command payloads, encode IP packet init and tag status, and add a small transfer for pipeline clear.

Control flow: `ipa_cmd_init()` performs build-time and runtime validation of header memory and register-write offsets. `ipa_cmd_pool_init()` creates a DMA-coherent payload pool on the command channel. Command add functions allocate a payload, fill little-endian hardware structs, and call `gsi_trans_cmd_add()` with the opcode. Pipeline clear builds a four-command sequence: no-op register write with full clear, packet-init to exception/LAN RX endpoint, tag-status command, and a zero-filled transfer, then waits for IPA completion.

State and persistence: Command payload memory is pooled in the command channel transaction info. The file itself has no globals. Runtime effects include IPA-local table/header content, register writes, DMA memory updates, and pipeline-clear completion state in `ipa->completion`.

Dependencies: Depends on GSI transactions, IPA core state, endpoint maps, memory descriptors, IPA register metadata, and IPA table hash support. It uses Linux bitfield helpers and DMA address types. Version branches handle v4+ pipeline-clear opcode fields and v5+ full-byte endpoint IDs.

Risks: Immediate-command payload encodings are hardware ABI. Offset/size fields are narrow and version-sensitive; validation must run before issuing commands. Command pool exhaustion should not occur if TRE reservations succeeded, so pool sizing must match `gsi_channel_tre_max()`. Pipeline clear depends on AP LAN RX endpoint being configured.

Test signals: Command init should reject oversized table/header/register offsets. Table init should work with and without hash regions. Pipeline clear should complete after modem/endpoint operations. DMA shared memory commands should read/write expected IPA-local regions. Watch for GSI command timeout and IPA completion stalls.
