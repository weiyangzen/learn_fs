## sources/control-plane/csi-driver-iscsi/hack/verify-yamllint.sh

Purpose: lints deploy and example YAML files.

Control flow installs `yamllint` with apt when missing, loops over `deploy/*.yaml` and `examples/*.yaml`, runs `yamllint -f parsable`, filters out `line too long`, writes `/tmp/yamllint.log`, prints remaining issues, and fails if any remain.

State is `/tmp/yamllint.log` and possible apt package installation. Dependencies are apt, yamllint, glob expansion, and shell tools. Risks include no strict mode, unquoted variables, shared temp log path, ignoring line-length issues globally, and package installation requiring privileges. Test signal is `verify-all.sh`.
