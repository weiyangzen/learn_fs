# sources/distributed-fs/ceph-client/drivers/misc/nsm.c

## Purpose
This virtio driver exposes the Amazon Nitro Secure Module. It provides a raw `/dev/nsm` ioctl for CBOR request/response messages and registers an hwrng provider backed by the NSM `GetRandom` command.

## Important APIs, types, and functions
Important structures are `nsm_data_req`, `nsm_data_resp`, `nsm_msg`, and `nsm`. CBOR helpers are `cbor_object_is_array()` and `cbor_object_get_array()`. Request/response paths are `fill_req_raw()`, `parse_resp_raw()`, `nsm_sendrecv_msg_locked()`, `fill_req_get_random()`, `parse_resp_get_random()`, `nsm_rng_read()`, and `nsm_dev_ioctl()`. Virtio lifecycle functions are `nsm_device_probe()`, `nsm_device_remove()`, and `nsm_device_init_vq()`.

## Control flow and state
Probe allocates `nsm`, creates the single virtqueue, initializes the mutex, registers an hwrng named `nsm-hwrng`, then registers miscdevice `/dev/nsm` mode `0666`. Raw ioctl copies a user `nsm_raw`, copies bounded request bytes into the shared message buffer, queues one outbuf and one inbuf, kicks the virtqueue, waits up to two minutes for completion, validates returned buffers, copies/truncates the response to userspace, and returns. hwrng uses the same locked virtqueue path with a fixed CBOR `GetRandom` request and parses the random byte array from a known CBOR envelope.

## State and persistence behavior
State is volatile and serialized by `nsm->lock`: one virtqueue, one completion, one reusable message buffer, miscdevice, and hwrng registration. No persistent data is stored. Random data and raw responses are transient.

## Dependencies and integration points
It depends on virtio core, virtqueues, hwrng, miscdevice, user-copy helpers, completions, and UAPI `linux/nsm.h`. It integrates with AWS Nitro hypervisor-provided virtio device ID `VIRTIO_ID_NITRO_SEC_MOD`.

## Risks and test signals
Risks include virtqueue cleanup after partial enqueue failure, long blocking waits, raw device mode `0666`, CBOR parser limitations, response truncation semantics, mutex handling on all exits, and remove ordering (`hwrng_unregister`, `del_vqs`, `misc_deregister`). Test signals include raw ioctl success/error, oversized request rejection, timeout path, hwrng reads, malformed GetRandom response parsing, virtqueue buffer-order validation, and module remove under no-active-io conditions.
