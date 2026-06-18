# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbmod.json

## Purpose

`skbmod.json` defines 18 tc-testing cases for the `skbmod` action. It validates Ethernet header modification syntax for destination MAC, source MAC, EtherType, MAC swapping, ECN marking, controls, cookies, listing/getting, deletion, flushing, and invalid parser paths.

## Important APIs, Types, and Schema

The file uses the standard tc-testing schema with `nsPlugin`. It exercises `$TC actions add|replace|del|flush|ls|get action skbmod`. The command grammar under test includes `set dmac <mac>`, `set smac <mac>`, `set etype <u16>`, `swap mac`, `ecn`, controls `pipe`, `reclassify`, `drop`, `continue`, and `pass`, plus `index` and `cookie`.

## Control Flow

Each case starts with clean or preloaded `skbmod` state, executes a command, then verifies with list or get. Positive tests assert normalized MAC casing, EtherType rendering, control action, index/ref, cookie, and list counts. Negative tests expect `255` and assert absence for invalid MAC length and out-of-range EtherType. Delete and flush tests assert removal of persisted actions.

## State and Persistence Behavior

State is the skbmod action entry in the kernel action table. Most adds use default index behavior unless an explicit index is supplied. Replacement with invalid goto-chain control starts from an existing pass action at index 90 and verifies the invalid replacement does not overwrite it. Delete removes a specific indexed action; flush removes all skbmod actions.

## Dependencies and Integration Points

The tests require `$TC`, `nsPlugin`, and skbmod support in kernel/iproute2. They validate action management and rendering only; no packet is sent to prove header rewriting or ECN modification on the datapath.

## Risks

Assertions are sensitive to output normalization, especially uppercase EtherType rendering (`0xFEFE`, `0xBEEF`) and lowercase MAC rendering for uppercase input. The suite does not test index bounds or batch behavior for skbmod, and it does not verify real packet mutation.

## Test Signals

Coverage includes setting destination and source MAC addresses, rejecting invalid MAC, setting valid EtherType, rejecting oversized EtherType, swapping MACs, all common controls, cookie rendering, listing five preloaded actions, getting a specific action by index, deleting an indexed action, flushing all actions, invalid goto-chain replace preservation, and adding the ECN modifier.
