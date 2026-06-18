<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.c

Purpose: central context/channel coordinator for pvrusb2. It serializes asynchronous hardware initialization, notification delivery, disconnect cleanup, channel ownership, input-limit arbitration, and MPEG stream wrapping.

Important APIs/types/functions: global lists track existing contexts and contexts needing notification. `pvr2_context_thread_func()` is the driver worker thread. `pvr2_context_create()`, `pvr2_context_disconnect()`, `pvr2_context_global_init()`, and `pvr2_context_global_done()` manage context lifetime. `pvr2_channel_init()`, `pvr2_channel_done()`, `pvr2_channel_limit_inputs()`, and `pvr2_channel_claim_stream()` manage user channels. `pvr2_channel_create_mpeg_stream()` creates an `ioread` wrapper with MPEG pack sync key.

Control flow: creating a context links it into the global existence list, creates hardware state, and enqueues notification. The global thread drains the notify list, initializes hardware in thread context, installs the video stream, invokes the setup callback, runs each channel check callback, and destroys a disconnected context once no channels remain. Channels attach to the context list, may claim the shared video stream exclusively, and can reduce allowed hardware inputs; input masks across channels are intersected and committed to hardware.

State and persistence: persistent state includes global context lists, notify flags, cleanup flags, the kernel thread, each `struct pvr2_context`, and each linked `struct pvr2_channel`. State is memory-only and tied to device lifetime.

Dependencies and integration: depends on pvrusb2 hardware, stream, and ioread layers plus waitqueues, kthreads, mutexes, and trace flags. V4L2, sysfs, and DVB frontends create channels through this layer.

Risks: global cleanup waits for all contexts to disappear before stopping the thread; leaked channels can block module unload. `pvr2_context_disconnect()` calls hardware disconnect before setting `disconnect_flag`, creating a short ordering window. Input-limit arbitration is subtle and depends on every channel clearing masks on teardown. `pvr2_channel_claim_stream()` kills any previously claimed stream when switching.

Test signals: module load/unload with multiple devices; disconnect while V4L2/DVB/sysfs channels are open; concurrent stream claim attempts returning `-EBUSY`; input-limit conflicts between analog and DVB paths; context trace logs for init/destroy ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.c -->
