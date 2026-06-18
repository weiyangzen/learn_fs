# sources/distributed-fs/ceph-client/include/linux/hugetlb_cgroup.h

## Purpose
Defines hugetlb cgroup accounting structures and charge/uncharge hooks for allocated huge pages and reservations.

## APIs, Control Flow, and State
With `CONFIG_CGROUP_HUGETLB`, `struct hugetlb_cgroup` embeds cgroup CSS state, per-hstate `page_counter` arrays for used and reserved huge pages, event counters, event files, and per-node usage. Folios hold separate allocation and reservation cgroup pointers accessed by `hugetlb_cgroup_from_folio()` and `_rsvd()` and set by `set_hugetlb_cgroup()` and `_rsvd()`. Reservation maps can hold CSS/page-counter metadata; dup/put helpers manage CSS references. The charge flow is charge cgroup, commit charge to folio or reservation, and uncharge on folio/free-region/reservation cleanup. Disabled builds turn accounting into no-ops and report `hugetlb_cgroup_disabled()` as true.

## Dependencies, Integration, Risks, and Tests
Depends on hugetlb folios, `struct resv_map`, `struct file_region`, cgroup CSS, and page counters. It integrates with hugetlb allocation, reservation creation, reservation map duplication/release, file-region deletion, and migration. Risks are mismatched reservation vs allocation cgroup pointers, lost CSS references, uncharging the wrong hstate index or page count, and assuming accounting exists in non-cgroup builds. Test signals include hugetlb cgroup limit enforcement, reservation accounting tests, migration preserving cgroup state, cgroup event counters, and config builds with and without `CONFIG_CGROUP_HUGETLB`.
