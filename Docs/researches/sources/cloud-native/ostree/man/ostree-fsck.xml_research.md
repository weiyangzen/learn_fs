# sources/cloud-native/ostree/man/ostree-fsck.xml

Purpose: documents `ostree fsck`, which validates repository object integrity.

Important APIs/types: options include checks such as deleting or verifying object state, plus fsverity-related validation noted in the page.

Control flow: walks repository objects and refs, verifies object checksums/metadata, and optionally repairs or deletes invalid data according to options.

State and persistence: normally read-only verification, but repair/delete modes mutate repository object state.

Dependencies and integration: integrates object storage, checksums, commit metadata, fsverity, and repository maintenance workflows.

Risks and test signals: risks include destructive repair options and expensive full-repo scans. Signals are fsck tests with corrupted objects, missing objects, valid repos, and fsverity metadata.
