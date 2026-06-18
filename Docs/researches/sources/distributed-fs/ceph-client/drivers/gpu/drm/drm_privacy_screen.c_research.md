# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen.c

Purpose: implements the DRM privacy-screen class used by non-KMS provider drivers and KMS connector consumers to expose standard privacy-screen properties and state notifications.

Important APIs/types/functions: global lookup and device lists are guarded by `drm_privacy_screen_lookup_lock` and `drm_privacy_screen_devs_lock`. `drm_privacy_screen_lookup_add()` and `drm_privacy_screen_lookup_remove()` manage static provider lookup entries. `drm_privacy_screen_get()` resolves a consumer device/connector to a provider, and `drm_privacy_screen_put()` drops the reference. `drm_privacy_screen_set_sw_state()`, `drm_privacy_screen_get_state()`, notifier register/unregister helpers, `drm_privacy_screen_register()`, `drm_privacy_screen_unregister()`, and `drm_privacy_screen_call_notifier_chain()` are the provider/consumer API surface. Sysfs exposes read-only `sw_state` and `hw_state`.

Control flow: consumers resolve lookup entries with clock-framework-style fuzzy matching, preferring dev+connector over dev-only over connector-only. Provider registration allocates a `drm_privacy_screen`, initializes locking and notifier state, queries initial hardware state through provider ops, registers a class device, then adds it to the provider list. Software state setting stores requested state when hardware is locked or already matching; otherwise it calls provider `set_sw_state`. Unregister removes the device from lookup visibility, clears ops/data under lock, then unregisters the class device.

State and persistence behavior: lookup entries are owned by callers and must outlive list membership. Provider devices persist in the DRM class until `device_unregister()` release frees them. Each privacy screen stores `sw_state`, `hw_state`, provider ops/data, a notifier chain, and class-device sysfs state.

Dependencies and integration points: integrates `drm_privacy_screen_machine.h`, consumer and driver privacy-screen APIs, DRM class sysfs, provider drivers such as platform/x86 implementations, and connector helpers that attach/update privacy-screen connector properties.

Risks: provider lookup is static and not firmware-node based yet, so mismatched names can cause `-ENODEV` or indefinite `-EPROBE_DEFER`. Provider `get_hw_state()` is called during registration and must initialize states correctly. Notifiers are deliberately not called for `set_sw_state()`, so drivers must emit external-change notifications themselves. Clearing ops during unregister means readers must honor `-ENODEV` paths.

Test signals: provider register/unregister lifetime, lookup specificity ordering, deferred probe before provider registration, locked hardware state preserving requested software state, sysfs state reads, notifier callbacks for external changes, and connector property integration tests.
