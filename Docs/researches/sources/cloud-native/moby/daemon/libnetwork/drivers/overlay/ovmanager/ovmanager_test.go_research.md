# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager_test.go

Purpose: Tests overlay VNI allocator behavior for automatic and user-defined allocations.

Important APIs and functions: `parseCIDR` builds IPAM pools. `TestNetworkAllocateFree` allocates two subnets and confirms two returned VNI IDs, then frees the network. `TestNetworkAllocateUserDefinedVNIs` supplies three VNIs for two subnets and verifies the returned list contains exactly the first two.

Control flow: tests use `newDriver` directly and inspect returned option map.

State and persistence: in-memory allocator only.

Dependencies and integration points: validates `NetworkAllocate`/`NetworkFree` and netlabel VNI option output.

Risks: does not test duplicate VNI rejection, duplicate network ids, allocation exhaustion, or invalid VNI parse errors.

Test signals: useful coverage for common allocation paths and normalized output count.
