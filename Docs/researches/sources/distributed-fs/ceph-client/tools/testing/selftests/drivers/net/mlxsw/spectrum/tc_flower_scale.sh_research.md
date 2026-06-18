<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_flower_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_flower_scale.sh

Purpose: Spectrum-1 target provider for generic tc flower scale testing with a fixed theoretical ACL-rule target.

Important functions/APIs: sources `../tc_flower_scale.sh`; defines `tc_flower_get_target` with hard-coded normal target `5631`.

Control flow: normal mode returns 5631, derived from theoretical 6144 rules minus one 512-rule bank and one catch-all; overflow mode returns 5632.

State/dependencies: stateless but assumes Spectrum-1 ACL bank layout. Risks include hard-coded capacity mismatch under different profiles or firmware. Test signals are inherited flower batch insertion, `in_hw` counting, and traffic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_flower_scale.sh -->
