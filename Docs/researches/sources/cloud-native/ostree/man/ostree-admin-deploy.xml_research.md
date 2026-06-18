# sources/cloud-native/ostree/man/ostree-admin-deploy.xml

Purpose: documents `ostree admin deploy`, which checks out a revision/refspec as a new deployment and normally makes it default on next boot.

Important APIs/types: required `REFSPEC`; options `--stateroot`, `--os`, `--origin-file`, `--retain`, `--retain-pending`, `--retain-rollback`, `--not-as-default`, `--lock-finalization`, `--karg-proc-cmdline`, `--karg`, `--karg-append`, and `--karg-delete`.

Control flow: command creates a deployment, processes `/etc`, updates boot configuration/default ordering unless append mode is selected, applies kernel args, and can lock finalization for staged deployment workflows.

State and persistence: writes deployment directories, origin metadata, bootloader configuration, kernel argument state, and retained deployment set.

Dependencies and integration: central admin integration point with sysroot, repo refs, origin files, boot config, finalization locking, and `ostree admin status`.

Risks and test signals: high-risk boot state mutation; docs must reflect retention/default/finalization semantics. Signals are admin deployment integration tests, bootloader entries, status output, and rollback/pending retention tests.
