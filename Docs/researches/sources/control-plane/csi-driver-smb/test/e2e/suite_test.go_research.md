# sources/control-plane/csi-driver-smb/test/e2e/suite_test.go

## Purpose
This is the Ginkgo/Gomega e2e suite bootstrap for the SMB CSI driver. It installs or reuses the SMB provisioner and CSI driver, starts an in-process SMB driver endpoint for direct CSI cleanup calls, configures test storage-class parameters, adapts Linux test commands for Windows clusters, and performs suite teardown/log collection.

## Important APIs, Types, And Functions
Key constants define environment-variable contracts: `KUBECONFIG`, `ARTIFACTS`, `TEST_WINDOWS`, `WINDOWS_SERVER_VERSION`, `PRE_INSTALL_SMB_PROVISIONER`, `TEST_SMB_SOURCE`, `TEST_SMB_SECRET_NAME`, and `TEST_SMB_SECRET_NAMESPACE`. Package globals hold `smbDriver`, Windows/preinstall flags, and storage-class parameter maps for default, subdir, retain, archive, and no-provisioner-secret modes. `testCmd` models an external command with start/end log messages. `BeforeSuite` and `AfterSuite` are the main lifecycle hooks. `TestMain` wires Kubernetes e2e flags, `TestE2E` runs specs with a JUnit reporter, `execTestCmd` runs project-root commands, `convertToPowershellCommandIfNecessary` maps known shell snippets to PowerShell, and `skipIfTestingInWindowsCluster` centralizes Windows skips.

## Control Flow
`BeforeSuite` ensures `KUBECONFIG`, optionally runs `make install-smb-provisioner`, `make e2e-bootstrap`, and `make create-metrics-svc`, then starts `smb.Driver.Run` against a random Unix socket. For Windows clusters it changes to the project root, obtains either an Azure File source for host-process deployments or the public SMB service IP, and rewrites all storage-class parameter maps. `AfterSuite` runs example validation for non-Windows clusters, always prints SMB logs, tears down the e2e driver unless preinstalled, and validates install/uninstall scripts.

## State, Persistence, And Dependencies
Persistent state is external: Kubernetes resources, generated JUnit XML under `ARTIFACTS` or `test/e2e`, and potential `/tmp/csi-*.sock` sockets. It depends on `make` targets, shell scripts under `test/utils`, Kubernetes e2e framework packages, Ginkgo v2, Gomega, and the SMB driver package.

## Integration Points
The suite supplies globals consumed by dynamic provisioning specs and testsuite structs. It integrates with Kubernetes via kubeconfig, with Makefile deployment targets, with Windows-specific helper scripts, and with the local CSI driver object used by reclaim-policy tests.

## Risks And Test Signals
Risks include process-wide `os.Chdir`, mutable global storage-class maps, hard-coded command translations, base64-encoded host-process test account data, and command failures surfaced only during suite startup/teardown. The primary test signals are Ginkgo spec results, JUnit output, Kubernetes events/logs from `smb_log.sh`, and direct Gomega expectations around external command success.
