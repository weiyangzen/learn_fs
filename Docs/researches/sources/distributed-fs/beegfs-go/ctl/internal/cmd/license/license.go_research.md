
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/license/license.go

- Purpose: implements `license`, including reload, display, license acquisition help, and URL generation.
- Important APIs: `license_Config`, `NewCmd`, `runLicenseCmd`, `printGenerateLicenseHelp`, `generateLicenseURL`, and `assembleGetArgs`.
- Control flow/state: gets/reloads license, preserves reload errors while still printing certificate data when possible, formats JSON or ASCII/table-like human output, checks expiration/violations, queries nodes for license URL parameters, and prints install guidance for missing/invalid licenses.
- Dependencies/integration: uses license and node backends, management/license protobufs, Viper/logging, URL encoding, unit formatting, and CTL error helpers.
- Risks/tests: complex error choreography around reload can confuse callers; output mixes compliance state and retrieval instructions. No direct tests in this subset.
