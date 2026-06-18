# sources/distributed-fs/juicefs/pkg/object/hdfs_kerberos.go


Purpose: supplies Kerberos authentication support for HDFS builds.

Important APIs and flow: `getKerberosClient` loads krb5 config from `KRB5_CONFIG` or `/etc/krb5.conf`. It first tries keytab authentication from `KRB5KEYTAB_BASE64` or `KRB5KEYTAB` plus `KRB5PRINCIPAL`, splitting principal into username and realm. If no keytab is available, it loads a credential cache from `KRB5CCNAME`, stripping `FILE:` prefixes, or defaults to `/tmp/krb5cc_{uid}`. It returns a gokrb5 client from keytab or ccache.

State and persistence: reads host Kerberos config, keytab material, and ccache files. It does not write credentials.

Dependencies and integration: used by `newHDFS` when Hadoop client options already indicate Kerberos. Depends on `github.com/jcmturner/gokrb5/v8`.

Risks: `KRB5PRINCIPAL` must include `@realm` for keytab mode. Unsupported ccache schemes error. Base64 keytab data in environment is sensitive. Logging includes username and realm. Runtime behavior depends heavily on host Kerberos configuration.

Test signals: no direct tests in this subset; HDFS integration tests cover this only in a configured Kerberized environment.
