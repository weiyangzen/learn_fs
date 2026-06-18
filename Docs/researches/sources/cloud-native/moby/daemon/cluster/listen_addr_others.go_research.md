# Research: sources/cloud-native/moby/daemon/cluster/listen_addr_others.go

## sources/cloud-native/moby/daemon/cluster/listen_addr_others.go

Purpose: non-Linux implementation of `(*Cluster).resolveSystemAddr`. It delegates directly to `resolveSystemAddrViaSubnetCheck`.

There are no additional APIs or local state beyond the method. The integration point is swarm init/join advertise address autodetection on non-Linux platforms. Risk is that non-Linux platforms do not get the Linux netlink device filtering behavior and rely on the generic `net.Interfaces` path. Test coverage is indirect.
