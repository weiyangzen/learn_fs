# sources/cloud-native/containers-storage/storage.conf

Purpose: sample/default containers/storage configuration file documenting storage roots, driver selection, read-only image stores, pull behavior, auto-userns settings, and overlay driver options.

Important APIs/types/functions: TOML tables `[storage]`, `[storage.options]`, `[storage.options.pull_options]`, and `[storage.options.overlay]`. Active defaults include `driver = "overlay"`, `runroot = "/run/containers/storage"`, `graphroot = "/var/lib/containers/storage"`, empty `additionalimagestores`, and overlay `mountopt = "nodev"`.

Control flow: configuration precedence is documented in comments; actual parsing is handled by the `types` package and exposed through helpers in `store.go`.

State/persistence: defines persistent storage locations and behavior for engines using the library. Options can affect image/layer contents, metadata persistence, and mount behavior.

Dependencies/integration: consumed by containers/storage users such as Podman/Buildah through `types.Options`/config reload. Pull options integrate with zstd:chunked, hard links, ostree repos, and integrity policy.

Risks: comments warn that `force_mask` can expose files like `/etc/shadow` when set to shared permissions, and that `insecure_allow_unpredictable_image_contents` should almost never be enabled. Changing graphroot on SELinux systems requires relabeling.

Test signals: config parser tests should verify string-bool handling, precedence, overlay mount option extraction, rootless path expansion, and defaults matching this file.
