# sources/cloud-native/moby/contrib/nuke-graph-directory.sh

## Purpose
Safely destroys an old Docker graph directory by unmounting submounts and deleting btrfs subvolumes before removing files.

## APIs, Types, And Functions
The key helper is `dir_in_dir`. The script uses `readlink`, `/proc/self/mountinfo`, `umount -f`, optional `btrfs subvolume delete`, `find`, `stat`, shell globbing, and `rm -rf`.

## Control Flow, State, And Integration
The script requires a directory argument and root privileges, canonicalizes the target, prints a warning with a delay, unmounts nested mount points, deletes nested btrfs subvolumes, then removes all contents of the target directory.

## Risks And Test Signals
Risk is intentionally high because the script is destructive. Its safety controls are root check, canonicalization, delay, mount unrolling, and targeting contents rather than blindly crossing mount boundaries. Integration is with legacy Docker data-root cleanup.
