# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/zero.c

Purpose: `g_zero`, the development/test gadget with source/sink and loopback configurations for exercising UDC, composite, endpoint, suspend/resume, and remote wakeup behavior.

Important APIs, types, and functions: `gzero_options` stores bulk, isochronous, queue-depth, and pattern parameters. `zero_bind` gets `SourceSink` and `Loopback` function instances, copies module options into their option structs, assigns strings, configures OTG/autoresume behavior, adds both configurations, and attaches the functions. `ss_config_setup` forwards source/sink vendor control requests. `zero_suspend`, `zero_resume`, and `zero_autoresume` implement timed remote wakeup testing. `zero_unbind` deletes the timer and releases resources.

Control flow: bind creates two configurations in an order controlled by `loopdefault`, adds source/sink and loopback functions after endpoint autoconfig resets, and enables wakeup attributes when autoresume or OTG requires them. Suspend arms a timer; the timer calls `usb_func_wakeup` on superspeed-capable function paths or `usb_gadget_wakeup` otherwise. Resume deletes the timer.

State and persistence: module parameters define transient runtime behavior. `autoresume_timer`, `autoresume_cdev`, and `autoresume_step_ms` maintain wakeup-test state while bound. No durable state exists.

Dependencies and integration points: depends on libcomposite and `g_zero.h` function implementations for SourceSink and Loopback. It is designed to pair with host-side `usbtest` and descriptor/transfer test tools.

Risks: because this driver is used as a test oracle, descriptor/configuration ordering and wakeup behavior must stay stable. Timer lifetime must be synchronized on unbind. Parameter combinations for isochronous maxpacket/mult/burst and queue lengths can expose UDC limitations.

Test signals: run host `usbtest`, enumerate both configurations with `loopdefault` true/false, exercise source/sink control requests 0x5b/0x5c, run loopback bulk tests, vary pattern and buffer lengths, test isochronous options, suspend/resume with autoresume and max-autoresume stepping, and unload during idle and after suspend.
