## sources/cloud-native/moby/integration-cli/fixtures/credentialspecs/valid.json

Purpose: static Windows credential spec fixture representing a valid Group Managed Service Account configuration for integration tests that parse or submit credential specs.

Structure: top-level `CmsPlugins` contains `ActiveDirectory`; `DomainJoinConfig` supplies SID, machine account name, GUID, DNS tree/name, and NetBIOS name; `ActiveDirectoryConfig.GroupManagedServiceAccounts` lists the account name scoped to both `hyperv.local` and `hyperv`.

State is immutable fixture data. Dependencies are consumers that expect Docker credential-spec JSON schema shape and Windows/Active Directory semantics. Risks are schema drift, tests assuming exact whitespace-insensitive JSON fields, and the fixture being used on non-Windows paths without requirement gates. Test signals are successful JSON parsing and validation by credential-spec code; failures would usually be invalid field names, missing gMSA data, or malformed GUID/SID strings.
