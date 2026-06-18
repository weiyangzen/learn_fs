# sources/distributed-fs/ceph-client/net/9p/trans_usbg.c

Purpose: implements a USB gadget function and matching 9P transport named `usbg`, allowing a USB peripheral to mount a host-exported 9P filesystem over two bulk endpoints.

Important APIs, types, and functions: `struct f_usb9pfs` combines the 9P client, endpoint pointers, USB requests, completions, buffer length, and `usb_function`. `struct f_usb9pfs_opts` and `struct f_usb9pfs_dev` provide configfs instance state, tag selection, and in-use tracking. Transport entry points are `p9_usbg_create`, `p9_usbg_request`, `p9_usbg_cancel`, and `p9_usbg_close`; USB lifecycle functions include `usb9pfs_alloc_instance`, `usb9pfs_alloc`, `usb9pfs_func_bind`, `usb9pfs_set_alt`, `usb9pfs_disable`, and `usb9pfs_func_unbind`.

Control flow: configfs creates a tagged function instance and binds it into a composite USB configuration. Binding allocates interface IDs and autoconfigures IN/OUT bulk endpoints; `set_alt` enables endpoints and allocates one IN and one OUT request. A 9P mount selects the instance by tag and marks it in use. A request waits for the previous receive completion, queues the 9P request on the IN endpoint, waits for transmit completion, and queues the OUT request for the reply. RX completion parses the header, looks up the tag, bounds-checks against the response buffer, copies the reply, and calls `p9_client_cb`.

State and persistence: state is held in global `usbg_instance_list`, per-instance tags, an `inuse` flag, one request per endpoint, and `send`/`received` completions. The only user-visible persistent-ish configuration is configfs state while the gadget exists; it is not durable across module removal.

Dependencies and integration points: depends on USB composite/configfs APIs, endpoint descriptors for full/high/super speed, `DECLARE_USB_FUNCTION`, and v9fs transport registration. The `buflen` configfs attribute controls transport `maxsize` but cannot be changed once functions are referenced.

Risks: the implementation serializes requests through single IN/OUT USB requests, so concurrency assumptions are narrow. Prefix matching in `p9_usbg_create` uses `strncmp(devname, tag, strlen(devname))`, making ambiguous tag prefixes a risk. Completion and close paths must handle in-flight requests without double completion or leaked references. Disconnects can leave the client temporarily disconnected until endpoints are re-enabled.

Test signals: create multiple configfs instances with distinct and prefix-overlapping tags, bind/unbind at all supported speeds, mount while endpoints are disabled/enabled, send malformed or overlarge replies, kill waits, unplug during TX/RX, change `buflen` before/after reference, and run lockdep around spinlock and configfs mutex interactions.
