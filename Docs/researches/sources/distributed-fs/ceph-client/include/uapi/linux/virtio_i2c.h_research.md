<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_i2c.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_i2c.h

Purpose: defines the UAPI wire format for a virtio I2C adapter device, including message headers, feature negotiation, message flags, and backend status codes.

Important APIs and types: `VIRTIO_I2C_F_ZERO_LENGTH_REQUEST` advertises zero-length transfer support. `VIRTIO_I2C_FLAGS_FAIL_NEXT` groups requests with failure propagation, and `VIRTIO_I2C_FLAGS_M_RD` marks read transfers. `struct virtio_i2c_out_hdr` carries target address and flags; `struct virtio_i2c_in_hdr` carries `VIRTIO_I2C_MSG_OK` or `VIRTIO_I2C_MSG_ERR`.

Control flow, state, and persistence: guests enqueue one or more OUT headers and payload buffers and receive an IN status after host processing. The header stores no persistent state; device-visible state is transfer-local.

Dependencies and integration points: depends on Linux fixed-width and endian types, and integrates with virtio core and kernel I2C adapter emulation.

Risks and test signals: risks are flag misinterpretation, address endian bugs, and incorrect handling of grouped failures or zero-length transfers. Test read/write transfers, grouped multi-message transactions, NACK/error propagation, and feature-disabled zero-length requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_i2c.h -->
