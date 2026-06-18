# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lwt_dst_cache_ref_loop.sh

## Purpose
This shell test exercises lightweight tunnel encapsulation cases that historically could create dst-cache reference loops in lwtunnel input/output/xmit paths. It is explicitly a trigger script: kmemleak or kernel stability observation is needed to detect the bug.

## Important APIs and Functions
`check_compatibility` creates a temporary namespace, veth pair, loads `ila` if needed, attempts route encap setup for ILA, IOAM6, RPL, and SEG6, and records skip flags. `setup` creates three namespaces (`alpha`, `beta`, `gamma`) connected by two veth pairs with IPv6 forwarding through beta. `run_ila`, `run_ioam6`, `run_rpl`, and `run_seg6` install relevant encap routes and run ping6 traffic. `cleanup` removes namespaces and unloads `ila` if it was loaded by the script.

## Control Flow and State
The script requires root and `ip`, runs compatibility checks, installs an EXIT cleanup trap, builds the topology, confirms baseline ping reachability, then runs each encap case. It mutates namespace, route, sysctl, and module state; cleanup reverses namespace and optional module state but not global kmemleak state.

## Dependencies and Integration
It sources `lib.sh` for namespace helpers and kselftest exit codes. It depends on IPv6, veth, route encap support for ILA/IOAM6/RPL/SEG6, `modprobe`, and optional `kmemleak` monitoring outside the script.

## Risks and Test Signals
The script warns it may crash kernels lacking the loop-prevention fix. Its exit status is blindly pass after traffic attempts; absence of user-visible failure is not proof. Meaningful signals are kernel stability and external kmemleak results, while unsupported encap types print `SKIP:` lines.
