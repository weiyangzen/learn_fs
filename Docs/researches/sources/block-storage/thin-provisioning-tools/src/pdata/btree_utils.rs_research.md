# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_utils.rs

Contains `get_depth_` and `get_depth`, returning btree depth where `0` means root is a leaf. It reads/checks nodes, recurses through the first non-looping child that can reach a leaf, and skips path loops.

If all children fail, it returns the first captured error or a `NumEntriesTooSmall` node error. This utility is used by layered walkers to determine how many internal levels must be read.
