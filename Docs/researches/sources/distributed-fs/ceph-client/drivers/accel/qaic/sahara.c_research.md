# sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.c

Purpose: implements the Qualcomm Sahara firmware/image transfer and memory-debug protocol over `QAIC_SAHARA` MHI. It serves requested boot images from firmware files and collects Sahara memory dumps into devcoredump records.

Important APIs and types: public functions are `sahara_register` and `sahara_unregister`. Core types are `sahara_packet`, `sahara_debug_table_entry64`, `sahara_dump_table_entry`, `sahara_memory_dump_meta_v1`, and `sahara_context`. Static image tables map AIC100/AIC200 image IDs to firmware paths.

Control flow: probe selects AIC100 non-streaming or AIC200 streaming behavior, allocates RX/TX buffers, prepares MHI, and queues RX. Firmware commands are processed in workqueues: HELLO replies with supported version, READ_DATA finds and streams firmware chunks, END_OF_IMAGE releases active firmware and may send DONE, and MEMORY_DEBUG64 switches into host-driven memory reads. Dump parsing reads a firmware-provided table, validates lengths and strings, allocates a metadata+table+image buffer, reads each memory region in bounded chunks, and publishes it with `dev_coredumpv`.

State and persistence: `sahara_context` tracks active firmware, pending read offsets, dump table/device addresses, memdump buffer ownership, streaming mode, and RX sizes. State is per MHI device and removed with the channel.

Dependencies and integration: uses Linux firmware loader, MHI queueing, workqueues, overflow helpers, vmalloc, and devcoredump. It is registered from QAIC module init.

Risks and test signals: test missing optional firmware, image-id conflicts, overlong READ_DATA, streaming continuation, table overflow protection, EOI-as-error during memory read, RX requeue failures, and remove while dump or firmware work is active.
