# sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.h

## Purpose
`ldap-support.h` declares the optional LDAP credential integration for the Windows client service.

## Important APIs, Types, And Functions
It declares `PVFS_ldap_init`, `PVFS_ldap_cleanup`, and `get_ldap_credential(char *user_name, PVFS_credential *credential)`.

## Control Flow
The expected lifecycle is process startup initialization, credential lookup per cache miss/requestor, and process shutdown cleanup. The header itself does not enforce that lifecycle.

## State And Persistence
No state is declared here. Implementations use process-global LDAP library state and external global options.

## Dependencies And Integration Points
It includes `pvfs2.h` and `client-service.h`, so consumers have OrangeFS credential types and option definitions. In current service code, includes/calls are commented out, indicating an integration point rather than active behavior.

## Risks And Test Signals
Because LDAP mode is disabled in the current call path, declarations can drift from implementation unnoticed. No direct tests in the assigned client-test set validate this API.
