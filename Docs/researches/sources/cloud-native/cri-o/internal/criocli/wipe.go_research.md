# sources/cloud-native/cri-o/internal/criocli/wipe.go

Purpose: implements `crio wipe`, which removes CRI-O containers and optionally images after reboot/upgrade or when forced.

Important APIs/types/functions: `WipeCommand`, `crioWipe`, `ContainerStore`, `wipeCrio`, `getCrioContainersAndImages`, `deleteContainer`, and `deleteImage`.

Control flow: `crioWipe` loads config and storage, determines whether containers/images should be wiped from version files unless `--force` is set, handles unclean shutdown by removing the whole storage directory once and writing `/run/crio/crio-wipe-done`, exits early when internal wipe is enabled and not forced, skips if no container wipe is needed, then deletes CRI-O-owned containers and images. `getCrioContainersAndImages` scans storage containers, reads metadata, filters CRI-O containers, and records image IDs.

State and persistence behavior: reads version marker files and storage metadata. May remove the entire storage directory, unmount/delete containers, delete images, and write `/run/crio/crio-wipe-done`.

Dependencies/integration points: containers/storage, CRI-O config, internal storage metadata helpers, `lib.RemoveStorageDirectory`, and version wipe checks.

Risks: destructive by design. `os.ErrNotExist` from `Containers()` is returned despite being treated specially, which can propagate. Image IDs are not deduplicated before deletion. Running containers can make unmount/delete fail; failures are logged and deletion continues.

Test signals: no direct tests in this subset.
