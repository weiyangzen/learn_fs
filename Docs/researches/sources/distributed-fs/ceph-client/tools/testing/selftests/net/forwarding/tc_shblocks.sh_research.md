# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_shblocks.sh

Purpose: tests tc shared blocks (`ingress_block`/`egress_block`) and flower `indev` matching within a shared block across two switch ports.

Important functions are `shared_block_test` and `match_indev_test`. Setup creates two host interfaces and two switch interfaces with the same IP/MAC presentation, attaches clsact to `$swp1` and `$swp2` using `ingress_block 22 egress_block 23`, and normalizes `$swp2` MAC to `$swp1` for traffic symmetry.

Control flow checks shared block support, runs software mode and optionally offload mode. `shared_block_test` adds a filter to block 22 and verifies packets arriving through both ports hit the same counter. `match_indev_test` adds two block filters distinguished by `indev $swp1` vs `$swp2` and checks each packet hits the correct one. State is shared block filters, qdiscs, interface MAC override, and host VRFs. Risks include global block ID collisions, MAC restoration, and offload support. Test signals are exact `tc_check_packets "block 22"` counts and log entries for shared block and indev matching.
