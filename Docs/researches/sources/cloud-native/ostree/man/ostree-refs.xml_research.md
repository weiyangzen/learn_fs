# sources/cloud-native/ostree/man/ostree-refs.xml

Purpose: documents `ostree refs`, which lists, creates, aliases, or deletes refs.

Important APIs/types: forms `ostree refs [OPTIONS] [PREFIX]` and `ostree refs EXISTING --create=NEWREF`; options `--list`, `--create`, `--delete`, `--revision/-r`, `--alias/-A`, `--collections/-c`, and `--force`.

Control flow: default lists refs, optionally preserving full names with `--list`; create points a new ref/alias/mirrored collection ref at an existing commit; delete removes refs matching prefix/collection; revision mode adds checksums.

State and persistence: create/delete/force mutate repo ref storage; list is read-only.

Dependencies and integration: integrates commit lookup, ref namespaces, collection IDs, aliases, prune/admin cleanup for reclaiming objects, and scripting output.

Risks and test signals: risks include deleting broad prefixes, force overwrites, and collection refspec abuse. Signals are ref create/delete/list tests, alias tests, collection mode tests, and prune after delete.
