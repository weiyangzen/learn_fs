# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.c

Owns cx18 stream lifecycle for MPEG, TS, YUV, VBI, PCM, IDX, and radio. It prepares V4L2/DVB devices, initializes vb2 for YUV, allocates DMA queues, registers device nodes, starts/stops firmware capture tasks, and refills firmware MDLs with `cx18_out_work_handler`.

Important APIs include `cx18_streams_setup`, `cx18_streams_register`, `cx18_streams_cleanup`, `cx18_start_v4l2_encode_stream`, `cx18_stop_v4l2_encode_stream`, `cx18_stop_all_captures`, `cx18_stream_rotate_idx_mdls`, `cx18_find_handle`, and `cx18_handle_to_stream`. Startup creates a firmware task, sets channel type, configures shared encoder parameters, VBI, index and cx2341x controls, sets MDL ack offsets, loads MDLs, and starts capture. Stop releases MDLs, destroys the task, balances capture counters, and wakes waiters.

State includes stream flags, firmware handles, queues, vb2 lists/timers, `ana_capturing`/`tot_capturing`, VBI counters, and SCB MDLs. Dependencies include V4L2, vb2, cx2341x, cx25840 VBI subdevs, cx18 queues, mailbox APIs, and DVB support. Risks are shared firmware parameter ordering, failure unwinding, queue/timer locking, counter imbalance, and YUV/VBI size calculations. Test signals are streamon/streamoff, concurrent captures, IDX recycling, VBI mode changes, and DVB TS registration.
