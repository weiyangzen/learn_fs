# sources/distributed-fs/ceph-client/block/blk-cgroup-fc-appid.c

## Purpose

`blk-cgroup-fc-appid.c` stores and retrieves Fibre Channel application identifiers on block cgroups. It lets FC/app-ID plumbing associate a string with an I/O cgroup and lets bio users retrieve it through the bio's blkcg association.

## Important APIs, Types, And Functions

The file exports `blkcg_set_fc_appid()` and `blkcg_get_fc_appid()`. The setter accepts an app ID, cgroup ID, and length; the getter returns a direct `char *` to the blkcg stored ID or `NULL`.

## Control Flow, State, And Persistence

`blkcg_set_fc_appid()` validates `app_id_len` against `FC_APPID_LEN`, looks up the cgroup by ID, obtains the I/O controller CSS, converts it to `struct blkcg`, and copies the string into `blkcg->fc_app_id`. It drops CSS and cgroup references before returning. The write is intentionally lockless; the comment accepts that a racing I/O may miss a just-updated ID.

`blkcg_get_fc_appid()` returns `NULL` if the bio has no `bi_blkg` or the stored string is empty, otherwise returns the blkcg buffer.

## Dependencies And Integration Points

This file depends on `blk-cgroup.h`, `io_cgrp_subsys`, cgroup ID lookup, and the optional `fc_app_id` field in `struct blkcg`. Consumers are expected to call it after blkcg association has happened on the bio.

## Risks And Test Signals

Readers can see old or transient app IDs during lockless update, and the returned pointer is not a copy. Test valid and too-long IDs, missing cgroup IDs, missing I/O CSS, bios without `bi_blkg`, empty IDs, and concurrent set/get behavior.
