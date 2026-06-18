# sources/cloud-native/composefs-rs/examples/common/fix-verity/dracut-hook.sh

Purpose: initramfs hook run by the fix-verity EFI to enable fs-verity on composefs objects and `meta.json` inside `/sysroot/composefs`.

Important APIs/types/functions: `mount -o remount,rw /sysroot`, loop over `objects/*/*`, `fsverity enable`, `umount /sysroot`, `sync`, and `poweroff -ff`.

Control flow: remounts the target sysroot writable, enables verity on all composefs object files and metadata, unmounts, syncs, and powers off the VM.

State/persistence: mutates the disk image by enabling fs-verity metadata on files.

Dependencies/integration: depends on fsverity tool, mounted root partition, composefs repository layout, and QEMU boot from `fix-verity`.

Risks/test signals: glob misses or layout changes could leave unsealed files. Abrupt poweroff is intentional after sync but still sensitive to storage flushing.
