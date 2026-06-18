# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/hadoop-policy.xml

## Purpose
This test `hadoop-policy.xml` defines service authorization ACLs for Hadoop protocol tests. It is a permissive policy fixture for most services, with a self-user restriction for authorization refresh.

## Important Properties
The file sets `*` ACLs for `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.inter.datanode.protocol.acl`, `security.namenode.protocol.acl`, `security.inter.tracker.protocol.acl`, `security.job.submission.protocol.acl`, and `security.task.umbilical.protocol.acl`. `security.refresh.policy.protocol.acl` is set to `${user.name}`.

## Control Flow
There is no code, but Hadoop service-authorization code loads the policy and checks callers against the configured ACLs before allowing protocol access. The refresh policy entry exercises variable substitution and narrower authorization.

## State And Persistence
The file is static policy metadata. Runtime authorization state is held by Hadoop security managers and service authorization refresh code after loading this XML.

## Dependencies And Integration Points
It integrates with Hadoop RPC service authorization tests, NameNode/DataNode protocol ACL tests, MapReduce legacy protocol tests, and refresh-policy tests.

## Risks
The broad `*` ACLs are test conveniences and unsafe for production. If service property names drift from protocol implementations, tests may accidentally use defaults. Variable substitution in `${user.name}` must remain available for refresh policy tests.

## Test Signals
Signals include service-authorization acceptance for broad protocols, denial/allowance behavior for refresh-policy callers, and successful reload of authorization policy.
