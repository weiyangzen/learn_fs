# sources/distributed-fs/ceph-client/drivers/virtio/virtio_input.c

## Purpose
`virtio_input.c` implements the virtio input device driver. It maps a virtio input device into the Linux input subsystem, receives input events from the host, sends status events such as LED/sound updates back to the host, and supports suspend/resume.

## Important APIs, types, and functions
The main state is `struct virtio_input`, containing the virtio device, input device, identity strings, event and status virtqueues, a fixed event-buffer array, lock, and ready flag. Important functions are `virtinput_probe`, `virtinput_remove`, `virtinput_init_vqs`, `virtinput_fill_evt`, `virtinput_recv_events`, `virtinput_send_status`, `virtinput_recv_status`, `virtinput_status`, `virtinput_cfg_select`, `virtinput_cfg_bits`, `virtinput_cfg_abs`, and PM `virtinput_freeze`/`virtinput_restore`.

## Control flow
Probe requires modern virtio, allocates state, creates event/status queues, allocates an input device, reads name/serial/device IDs/properties/event bitmaps/absolute axis metadata from config space, initializes multitouch slots when advertised, marks the virtio device ready, registers the input device, and fills the event queue. Event callbacks drain host-provided event buffers, emit Linux `input_event` calls, recycle buffers, and kick the queue. Input core status callbacks allocate one status event, queue it to the host, and free it when the status queue completes.

## State and persistence
Runtime state includes config-derived input capabilities, queued event buffers, heap-allocated status buffers awaiting completion, and the `ready` flag protecting queue use during remove/freeze. No persistent state exists.

## Dependencies and integration points
It depends on virtio config/queues, Linux input and multitouch helpers, DMA cache-clean queue helper for device-written event buffers, and virtio input UAPI structures. It integrates host virtual keyboards, mice, tablets, and touch devices with evdev.

## Risks and test signals
Risks include malformed config bitmaps/axis sizes, event queue starvation, status buffer leaks on reset, races around `ready`, forwarding `MSC_TIMESTAMP` loops for multitouch, restore without re-registering capabilities, and host devices lacking `VIRTIO_F_VERSION_1`. Test signals include keyboard/mouse/tablet event streams, LED status updates, multitouch with timestamp filtering, config fuzzing, suspend/resume, remove with outstanding status buffers, and queue size larger than the fixed 64-event buffer pool.
