<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.h

## Purpose

`libsrp.h` declares the local SRP target helper interface and protocol constants shared by `libsrp.c` and `ibmvscsi_tgt.c`. It is not the kernel-wide SRP protocol header; it wraps Linux `<scsi/srp.h>` with IBM vSCSI target-specific queue and RDMA helper types.

## Important APIs, Types, and Constants

- Enumerations define CRQ valid values (`srp_valid`), payload formats (`srp_format`), init message formats (`srp_init_msg`), transport events (`srp_trans_event`), message statuses (`srp_status`), MAD version, OS type, SRP task attributes, and task-management response codes.
- `struct srp_buf` pairs a coherent buffer pointer with its DMA address.
- `struct srp_queue` contains IU pool storage and a locked `kfifo`.
- `struct srp_target` stores device pointer, command queue list, IU size, IU queue, receive ring, and caller-private `ldata`.
- `struct iu_entry` tracks one active IU buffer, including target pointer, remote token, flags, `sbuf`, and IU length.
- `srp_rdma_t` is the callback contract used by SRP descriptor helpers to move data between target scatterlists and client SRP memory descriptors.
- Public functions are `srp_target_alloc()`, `srp_target_free()`, `srp_iu_get()`, `srp_iu_put()`, `srp_transfer_data()`, `srp_data_length()`, and `srp_get_desc_table()`.
- `srp_cmd_direction()` returns `DMA_TO_DEVICE` when the high nibble of `buf_fmt` has a data-out descriptor; otherwise it returns `DMA_FROM_DEVICE`.

## Control Flow and State

The header defines the state objects consumed by the target implementation. A target allocates `srp_target`, obtains `iu_entry` objects for incoming CRQ payload copies, passes their SRP buffers into parser/Target Core paths, and returns them after the response is sent or the command is discarded. Data transfer flows through `srp_transfer_data()` into an `srp_rdma_t` callback supplied by the target driver.

## Dependencies and Integration Points

It includes Linux list and kfifo APIs plus `<scsi/srp.h>`. It forward-declares `struct ibmvscsis_cmd`, tying the generic-looking SRP helper to the IBM vSCSI target command type. Users must provide an RDMA callback matching the IBM target command structure.

## Risks and Edge Cases

- `srp_cmd_direction()` treats absence of data-out as data-in, so callers must separately handle no-data cases when that distinction matters.
- The enums mirror VIOSRP/IBM protocol values; mismatches with `<scsi/viosrp.h>` or firmware expectations break wire compatibility.
- `struct srp_target::cmd_queue` is declared here but command scheduling is mostly owned by `ibmvscsi_tgt.c`; ownership needs to remain clear.
- Because the RDMA typedef references `ibmvscsis_cmd`, this header is not a reusable generic SRP library boundary without refactoring.

## Test Signals

Build tests should catch enum/type drift with the C files. Runtime validation is indirect: successful target allocation, IU get/put cycling, SRP login, and read/write descriptor transfer all demonstrate that these declarations match the implementation and protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.h -->
