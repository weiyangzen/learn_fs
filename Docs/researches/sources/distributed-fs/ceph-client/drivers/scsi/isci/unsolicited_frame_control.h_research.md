# sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.h

Purpose: defines the data structures and sizing macros for ISCI SCU unsolicited-frame buffers, headers, and address tables.

Important APIs and types: `struct scu_unsolicited_frame_header` mirrors the hardware header word plus 15 dwords of received frame header data. `enum unsolicited_frame_state` tracks empty, in-use, released, and max states. `struct sci_unsolicited_frame` binds state, header pointer, and payload buffer. Header, buffer, and address-table array wrappers carry virtual arrays and DMA addresses. `struct sci_unsolicited_frame_control` aggregates the software get pointer plus those arrays. `SCI_UFI_BUF_SIZE`, `SCI_UFI_HDR_SIZE`, and `SCI_UFI_TOTAL_SIZE` define allocation sizing.

Control flow role: consumer code constructs the layout, retrieves headers/buffers by frame index, processes unsolicited arrivals, and releases frames using the prototypes declared here. The header’s first control word is explicitly separate from `data[]`, which is why `get_header()` returns `header->data`.

State and persistence: all fields describe DMA-backed runtime memory and software queue state. The hardware address table contains 64-bit DMA pointers to 1 KiB frame buffers; the state enum gates when software may advance the get pointer.

Dependencies and integration: depends on ISCI constants such as `SCU_MAX_UNSOLICITED_FRAMES` and `SCU_UNSOLICITED_FRAME_BUFFER_SIZE`, Linux `dma_addr_t`, and SCI status definitions.

Risks and test signals: structure layout and alignment must match silicon requirements. Watch for 32/64-bit DMA pointer assumptions, bitfield compiler layout, and stale frame states. Useful tests validate total allocation size, frame index bounds, and that release does not make a buffer reusable before older frames are processed.
