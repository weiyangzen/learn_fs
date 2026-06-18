# sources/distributed-fs/ceph-client/drivers/net/wan/framer/framer-core.c

Purpose: generic framer framework for E1/T1 line-interface components. It lets provider drivers create `struct framer` class devices and lets consumer drivers obtain, configure, power, monitor, and release those framers through OF phandles or parent lookup.

Important APIs, types, and functions: exported consumer APIs include `framer_init()`, `framer_exit()`, `framer_power_on()`, `framer_power_off()`, `framer_get_status()`, `framer_set_config()`, `framer_get_config()`, notifier registration helpers, `framer_get()`, `framer_put()`, and devm variants. Provider APIs include `framer_create()`, `framer_destroy()`, `devm_framer_create()`, `framer_provider_simple_of_xlate()`, `__framer_provider_of_register()`, and devm unregister helpers. Internal state uses the framer class, provider list, IDA IDs, mutex-protected init/power counts, work items, notifier chains, runtime PM, and optional regulator.

Control flow: providers create a framer device, optionally register an OF provider, and supply operations. Consumers resolve a framer, get device/module references, create a stateless device link, call init, optionally configure, power on/off, register notifiers, and release resources. If provider ops request `FRAMER_FLAG_POLL_STATUS`, `framer_init()` captures initial status and schedules periodic polling; changes trigger blocking notifier events. Direct status notifications from atomic context are deferred through workqueue.

State and persistence: state is in memory: init/power reference counts, previous status, notifier list, work items, class device lifetime, provider list, and regulator/runtime PM state. No disk persistence exists. Lifetime is reference-counted with device model and devres.

Dependencies and integration points: depends on Linux device model, class devices, OF phandle parsing, module references, device links, runtime PM, regulators, workqueues, IDA, mutexes, and blocking notifiers. PEF2256 is a provider; QMC HDLC is a consumer.

Risks: `framer_exit()` decrements `init_count` without visible underflow guard, so consumer call ordering matters. `framer_power_off()` similarly assumes balanced power calls. Provider lookup returns `-EPROBE_DEFER` for missing providers, which is correct for probe ordering but can hide permanent DT errors until later. Polling work reschedules unconditionally until cancelled, making balanced `framer_exit()`/destroy important.

Test signals: provider create/destroy, OF phandle and parent lookup, optional `devm_framer_optional_get()`, balanced and unbalanced init/power call behavior, notifier delivery from polling and explicit status change, runtime PM disabled/enabled paths, optional regulator enable/disable, provider unregister while consumers are absent, and module refcount behavior.
